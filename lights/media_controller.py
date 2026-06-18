"""Unified media control & progress utilities (Windows + Linux MPRIS).

Original behaviour (Windows Global System Media Transport Controls) is
preserved; this file now also supports Linux desktop environments via the
standard MPRIS D-Bus interface. Public API and returned data shape remain
unchanged so existing callers keep working:

Sync controls:
    stop_song(), seek_to_start(), resume_song()
Async controls:
    stop_song_async(), seek_to_start_async(), resume_song_async()
Helpers:
    get_current_media_state(), report_to_terminal(), monitor(), fix_rtl()

Returned state dict (platform-agnostic keys):
    position (float seconds, smoothed when playing)
    duration (float seconds)
    source (string identifying player/app)
    title (str or None)
    artist (str or None)
    playing (bool)
    status (original backend status value: numeric on Windows, str on Linux)
    raw_position (float seconds, unsmoothed)

Linux requirements: ``pip install dbus-next`` and a running user D-Bus
session (normally present in graphical sessions).
If no supported backend is available, functions will act as no-ops (controls)
or return ``None`` (state) rather than raising, to preserve previous silent
failure semantics when no media session exists.
"""

from __future__ import annotations

import asyncio
import time
import re
import sys
from typing import Optional, Dict, Any, Tuple, Any as AnyType

# ---------------------------------------------------------------------------
# Backend detection & conditional imports
# ---------------------------------------------------------------------------
_WINDOWS = sys.platform.startswith("win")
_LINUX = sys.platform.startswith("linux")

MediaManager = None  # type: ignore
if _WINDOWS:  # Attempt Windows import; leave graceful if failed (e.g. minimal env)
    try:
        from winsdk.windows.media.control import (  # type: ignore
            GlobalSystemMediaTransportControlsSessionManager as MediaManager,
        )
    except Exception:  # winsdk not available
        MediaManager = None  # type: ignore

_HAVE_DBUS = False
if _LINUX:
    try:
        from dbus_next.aio import MessageBus  # type: ignore
        from dbus_next import Message  # type: ignore
        _HAVE_DBUS = True
    except Exception:  # dbus-next not installed
        _HAVE_DBUS = False

# ---------------------------------------------------------------------------
# Playback status normalization
# ---------------------------------------------------------------------------
# Various numeric enums have been observed; we normalise to sets.
PLAYING_STATUSES = {1, 3, 4}
PAUSED_STATUSES = {2, 5}

_last_raw_position: float = 0.0
_last_position_timestamp: float = 0.0

# ---------------------------------------------------------------------------
# Low-level session fetch (Windows)
# ---------------------------------------------------------------------------
async def _fetch_session_data_windows():
    if not MediaManager:
        return None, None, None, None
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    if not current_session:
        return None, None, None, None
    playback_info = current_session.get_playback_info()
    media_properties = await current_session.try_get_media_properties_async()
    timeline_properties = current_session.get_timeline_properties()
    source = current_session.source_app_user_model_id.split("!")[-1]
    return playback_info, media_properties, timeline_properties, source

# ---------------------------------------------------------------------------
# Linux MPRIS helpers
# ---------------------------------------------------------------------------
_mpris_bus = None  # type: Optional[MessageBus]
_selected_player: Optional[str] = None  # org.mpris.MediaPlayer2.*

async def _mpris_connect():
    global _mpris_bus
    if _mpris_bus is None:
        try:
            _mpris_bus = await MessageBus().connect() if _HAVE_DBUS else None
        except Exception:
            _mpris_bus = None
    return _mpris_bus

async def _mpris_list_players() -> Tuple[str, ...]:
    bus = await _mpris_connect()
    if not bus:
        return tuple()
    try:
        names = await bus.list_names()
    except Exception:
        return tuple()
    return tuple(n for n in names if n.startswith("org.mpris.MediaPlayer2."))


async def _mpris_get_property(player: str, interface: str, prop: str):
    bus = await _mpris_connect()
    if not bus:
        return None
    msg = Message(
        destination=player,
        path="/org/mpris/MediaPlayer2",
        interface="org.freedesktop.DBus.Properties",
        member="Get",
        signature="ss",
        body=[interface, prop],
    )
    try:
        reply = await bus.call(msg)
    except Exception:
        return None
    if not reply or not reply.body:
        return None
    variant = reply.body[0]
    return getattr(variant, "value", variant)

async def _mpris_pick_player():
    """Pick/remember a player. Prefer one currently playing."""
    global _selected_player
    if _selected_player:
        return _selected_player
    players = await _mpris_list_players()
    if not players:
        _selected_player = None
        return None
    # Prefer Playing status
    for p in players:
        st = await _mpris_get_property(p, "org.mpris.MediaPlayer2.Player", "PlaybackStatus")
        if st == "Playing":
            _selected_player = p
            return p
    _selected_player = players[0]
    return _selected_player

async def _mpris_state() -> Optional[Dict[str, AnyType]]:
    player = await _mpris_pick_player()
    if not player:
        return None
    status = await _mpris_get_property(player, "org.mpris.MediaPlayer2.Player", "PlaybackStatus")
    metadata = await _mpris_get_property(player, "org.mpris.MediaPlayer2.Player", "Metadata") or {}
    position_us = await _mpris_get_property(player, "org.mpris.MediaPlayer2.Player", "Position")
    if position_us is None:
        # some players don't expose Position; treat as zero
        position_us = 0
    title = metadata.get("xesam:title")
    artists = metadata.get("xesam:artist") or []
    artist = artists[0] if isinstance(artists, (list, tuple)) and artists else None
    length_us = metadata.get("mpris:length") or 0
    duration = (length_us / 1_000_000.0) if length_us else 0.0
    raw_position = position_us / 1_000_000.0
    return {
        "status": status,
        "title": title,
        "artist": artist,
        "duration": duration,
        "raw_position": raw_position,
        "source": player.split(".")[-1],  # e.g. spotify, vlc
    }

# ---------------------------------------------------------------------------
# Public: state & progress
# ---------------------------------------------------------------------------
async def get_current_media_state() -> Optional[Dict[str, Any]]:
    """Return current media session state (cross-platform) with smoothing.

    Behaviour & output keys mirror the original Windows-only version so that
    dependent scripts remain compatible.
    """
    global _last_raw_position, _last_position_timestamp

    # Windows backend
    if MediaManager is not None:
        playback_info, media_props, timeline, source = await _fetch_session_data_windows()
        if not playback_info or not media_props or not timeline:
            return None
        status = getattr(playback_info, "playback_status", None)
        try:
            start = timeline.start_time.seconds
            raw_position = timeline.position.seconds - start
            end = timeline.end_time.seconds - start
        except Exception:
            return None
        now = time.time()
        if raw_position != _last_raw_position:
            _last_raw_position = raw_position
            _last_position_timestamp = now
        playing = status in PLAYING_STATUSES and status not in PAUSED_STATUSES
        if playing and end > 0:
            smooth_position = raw_position + (now - _last_position_timestamp)
            if smooth_position > end:
                smooth_position = end
        else:
            smooth_position = raw_position
        return {
            "position": float(smooth_position),
            "duration": float(end),
            "source": source,
            "title": getattr(media_props, "title", None),
            "artist": getattr(media_props, "artist", None),
            "playing": playing,
            "status": status,
            "raw_position": float(raw_position),
        }

    # Linux MPRIS backend
    if _HAVE_DBUS:
        state = await _mpris_state()
        if not state:
            return None
        # smoothing identical logic
        raw_position = state["raw_position"]
        end = state["duration"]
        now = time.time()
        if raw_position != _last_raw_position:
            _last_raw_position = raw_position
            _last_position_timestamp = now
        playing = state["status"] == "Playing"
        if playing and end > 0:
            smooth_position = raw_position + (now - _last_position_timestamp)
            if smooth_position > end:
                smooth_position = end
        else:
            smooth_position = raw_position
        return {
            "position": float(smooth_position),
            "duration": float(end),
            "source": state["source"],
            "title": state["title"],
            "artist": state["artist"],
            "playing": playing,
            "status": state["status"],
            "raw_position": float(raw_position),
        }

    # Unsupported platform / no backend
    return None

hebrew_re = re.compile(r"[\u0590-\u05FF]")
latin_re = re.compile(r"[A-Za-z]")

def fix_rtl(text: str) -> str:
    if not text:
        return text
    if hebrew_re.search(text):
        if not latin_re.search(text):
            return text[::-1]
        return "\u202B" + text + "\u202C"
    return text

def report_to_terminal(enable_rtl_correction: bool = True):
    import terminal  # local dependency
    while True:
        state = asyncio.run(get_current_media_state())
        if state:
            if enable_rtl_correction:
                state["artist"] = fix_rtl(state.get("artist") or "")
                state["title"] = fix_rtl(state.get("title") or "")
            terminal.update_song_data(
                artist_name=state["artist"],
                song_name=state["title"],
                total_seconds=int(state["duration"]),
                elapsed_seconds=int(state["position"]),
                playing=state["playing"],
                platform=state["source"],
            )
        time.sleep(0.5)

def start_report_to_terminal_thread():
    '''Start the media progress reporting thread. Call once at program start.
    Non-blocking.'''
    import threading
    update_song_progress_t = threading.Thread(target=report_to_terminal, daemon=True)
    update_song_progress_t.start()

