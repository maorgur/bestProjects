//ID:217280973

import java.awt.*;
import java.util.Arrays;

import exe.ex3.game.Game;
import exe.ex3.game.GhostCL;
import exe.ex3.game.PacManAlgo;
import exe.ex3.game.PacmanGame;

/**
 * This is the major algorithmic class for Ex3 - the PacMan game:
 *
 * This code is a very simple example (random-walk algorithm).
 * Your task is to implement (here) your PacMan algorithm.
 */
public class Ex3Algo implements PacManAlgo {
	private int _count;
	public Ex3Algo() {_count=0;}
	@Override
	/**
	 *  Add a short description for the algorithm as a String.
	 */
	public String getInfo() {
		return null;
	}

	final int code = 0;

	int blue = Game.getIntColor(Color.BLUE, code);
	int pink = Game.getIntColor(Color.PINK, code);
	int green = Game.getIntColor(Color.GREEN, code);
	int black = Game.getIntColor(Color.BLACK, code);

	Index2D target = new Index2D(11, 14); //starting pacman position, forcing to change a target
	GhostCL[] ghosts;
	boolean isEatable; //if the ghosts are eatable FOUND BUG: when changing speed, the time that it is possible to it ghost is still based on realtime and doesn't change
	Index2D closestGhost; //the distance to the closest ghost to chase him

	boolean foundGhostEscape; //if found a new target when running away from ghosts


	@Override
	public int move(PacmanGame game) {

		//get info
		Index2D pacmanPos = convertStringToIndex2D(game.getPos(code));
		Map board = new Map(game.getGame(code));
		board.setCyclic(game.isCyclic());
		ghosts = game.getGhosts(code);

		isEatable = ghosts[0].remainTimeAsEatable(code) > 1; //one second so the pacman has time to escape

		closestGhost = new Index2D(-1, -1); //find the closest ghost to chase
		foundGhostEscape = false;
		for (GhostCL ghost : ghosts) {
			Index2D ghost2D = convertStringToIndex2D(ghost.getPos(code));
			if (!isEatable) {
				//if a ghost is close to the pacman, get a new target that escapes from the ghosts from furthestGhosts

				int radius = 0; //define how close a ghost needs to be
				if (ghost.getStatus() == 1) { //the ghost is active

					if (ghost.getType() <= 11) {radius = 4;} //random moving ghosts
					else {radius = 7;} //shortestPath ghosts
				}

				if (board.shortestPath(ghost2D, pacmanPos, blue).length <= radius) { //if close

					if (furthestGhosts(board, pacmanPos, ghosts) != null) {
						System.out.println("escaping");
						foundGhostEscape = true;
						target = (Index2D) furthestGhosts(board, pacmanPos, ghosts);
					} else {
						return game.ERR; //everywhere that the pacman will go - it will be worse
					}
					break;
				}

			} else { //eatable

				//find the closest ghost
				if (ghost.getStatus() == 1 && !pacmanPos.equals(new Index2D(11, 11)) && //ignore inactive ghosts and ghosts that just spawned and not moved yet
						ghost.getType() != 11 //this type of ghosts are the type that going full speed, it takes too much time to catch up to them
				)
				{
					try { //if the closest ghost has not been set yet
						if (board.shortestPath(pacmanPos, closestGhost, blue).length > board.shortestPath(pacmanPos, ghost2D, blue).length) {
							target = new Index2D(ghost2D);
						}
					} catch (IndexOutOfBoundsException e) {closestGhost = new Index2D(ghost2D);}
				}
			}
		}

		if (isEatable && !closestGhost.equals(new Index2D(-1, -1))) { //assign target to the closest ghost
			System.out.println("chasing ghosts");
			target = closestGhost;
		}



		Map distanceMap = (Map) board.allDistance(pacmanPos, blue);
		//find a new target
		if ((distanceMap.getPixel(target) == black || pacmanPos.equals(target)) && !foundGhostEscape) { //if the target has reached or target is black
			boolean foundNewTarget = false;

			/*
			first, it will check all the blocks in a radius of 1 if they are pink or green
			if not, it will increment the radius and check again

			when found, the target will be set to it
			 */
			int iteration = 1;
			while (!foundNewTarget) {
				for (int x = 0; x < board.getWidth(); x++) {
					for (int y = 0; y < board.getHeight(); y++) {
						if (distanceMap.getPixel(x, y) == iteration) { //if pixel is in the current iteration

							if (board.getPixel(x, y) == pink || board.getPixel(x,y) == green){ //if green or pink, set target
								target = new Index2D(x, y);
								foundNewTarget = true;
								break;
							}
						}
					}
					if (foundNewTarget) {
						break;
					}
				}
				iteration ++;
			}
		}

		//go to target

		System.out.println("going to a point at " + target.toString());
		Index2D nextPos = (Index2D) board.shortestPath(pacmanPos, target, blue)[0]; //find the next move

		int[] offset = {pacmanPos.getX() - nextPos.getX(), pacmanPos.getY() - nextPos.getY()}; //how much is needed to move in each direction

		if (Math.abs((offset[0])) > 1 || Math.abs(offset[1]) > 1) { //if the distance is greater than 1, flip it because it tries to do a cyclic move
			offset[0] = offset[0] * -1;
			offset[1] = offset[1] * -1;
		}

		//move
		if (offset[1] < 0) {
			return game.UP;
		} else if (offset[0] > 0) {
			return game.LEFT;
		} else if (offset[0] < 0) {
			return game.RIGHT;
		} else if (offset[1] > 0) {
			if (pacmanPos.equals(new Index2D(11, 13))) {return game.ERR;} //block the pacman from ever going into the ghost spawn area and die, instead stall
			return game.DOWN;
		}

		return game.ERR;
	}

	private Pixel2D furthestGhosts(Map board, Index2D pacMan2D, GhostCL[] ghosts) {
		/*
		finds a new target to go that is the furthest from the ghosts
		there is a slight preference to pink/green targets
		the path
		 */

		double ghostDivider;

		//creates a map with the distance to the closest ghost
		Map totalDistance = new Map(board.getWidth(), board.getHeight(), 1000);

		//creates a map for every ghost, and then adds it to totalDistance
		Map tempGhostDistance;
		for (GhostCL ghost : ghosts) {
			if (ghost.getStatus() != 1) {break;} //ignore inactive ghosts

			ghostDivider = ghost.getType() < 12 ? 1 : 1.5; //if the ghost is moving randomly, it is moving 50% slower

			//write distance to totalDistance
			tempGhostDistance = (Map) board.allDistance(convertStringToIndex2D(ghost.getPos(code)), blue);
			for (int x = 0; x < board.getWidth(); x++) {
				for (int y = 0; y < board.getHeight(); y++) {
					if (totalDistance.getPixel(new Index2D(x, y)) > tempGhostDistance.getPixel(new Index2D(x, y)) / ghostDivider) {
						totalDistance.setPixel(new Index2D(x, y), (int) (tempGhostDistance.getPixel(new Index2D(x, y)) / ghostDivider));

					}
				}
			}
		}

		//find which position is the furthest and the pacman can go to
		int[] best = new int[]{0, 0, 0}; //X, Y, value
		for (int x = 0; x < board.getWidth(); x++) {
			for (int y = 0; y < board.getHeight(); y++) {
				if ( board.getPixel(x,y) != blue && (
						//if the checked pos is on a pink/green point, give it preference by saying it is 5 blocks further
						((board.getPixel(x,y) == pink || board.getPixel(x,y) == green)  && !(board.getPixel(best[0],best[1]) == pink || board.getPixel(best[0],best[1]) == green) && totalDistance.getPixel(x, y)+5 >= best[2]) ||
								((board.getPixel(x,y) == pink || board.getPixel(x,y) == green)  == (board.getPixel(best[0],best[1]) == pink || board.getPixel(best[0],best[1]) == green) && totalDistance.getPixel(x, y) > best[2]) //if there is no preference
				)) {

					//check if the path is not blocked by a ghost
					boolean isValid = true;
					try {
						for (Pixel2D pixel : board.shortestPath(pacMan2D, new Index2D(x, y), blue)) {
							if ((totalDistance.getPixel(pixel) < totalDistance.getPixel(pacMan2D)) //if the position is closer to ghosts
									|| pixel.equals(new Index2D(11, 13))) { //stop from trying to go into the ghost spawn area
								isValid = false;
								break;

							}

						}
					} catch (NullPointerException e) { //if there is no valid path, shortestPath returns null
						break;
					}
					if (isValid) { //set values
						best[0] = x;
						best[1] = y;
						best[2] = totalDistance.getPixel(new Index2D(x, y));
					}
				}
			}
		}
		if (Arrays.equals(best, new int[]{0, 0, 0})) {return null;} //if not found a better point to go
		return new Index2D(best[0], best[1]);
	}


	/*
	convert string of "X, Y" to Index2D object
	 */
	private Index2D convertStringToIndex2D(String pos) {return new Index2D(Integer.parseInt(pos.split(",")[0]), Integer.parseInt(pos.split(",")[1]));}


}
