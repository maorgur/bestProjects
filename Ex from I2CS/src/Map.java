//ID:217280973
import java.util.Arrays;

/**
 * This class represents a 2D map as a "screen" or a raster matrix or maze over integers.
 * @author boaz.benmoshe
 *
 */
public class Map implements Map2D {
	private int[][] _map;
	private boolean _cyclicFlag = true;

	/**
	 * Constructs a w*h 2D raster map with an init value v.
	 * @param w
	 * @param h
	 * @param v
	 */
	public Map(int w, int h, int v) {init(w,h, v);}
	/**
	 * Constructs a square map (size*size).
	 * @param size
	 */
	public Map(int size) {this(size,size, 0);}

	/**
	 * Constructs a map from a given 2D array.
	 * @param data
	 */
	public Map(int[][] data) {
		init(data);
	}
	@Override
	public void init(int w, int h, int v) {
		/////// add your code below ///////
		this._map = new int[w][h];
		//iterate over each index and set it to v
		for (int y = 0; y < this.getHeight(); y++) {
			for (int x = 0; x < this.getWidth(); x++) {
				this._map[x][y] = v;
			}
		}
		///////////////////////////////////
	}
	@Override
	public void init(int[][] arr) {
		/////// add your code below ///////
		if (arr == null || arr.length == 0) {
			throw new RuntimeException("array cannot be empty");
		}
		//check if ragged
		int arrLength = arr[0].length;
		for (int[] v: arr) {
			if (v.length != arrLength) {
				throw new RuntimeException("array cannot be a ragged array");
			}
		}

		this._map = Arrays.copyOf(arr, arr.length); //does a deep copy of arr

		///////////////////////////////////
	}
	@Override
	public int[][] getMap() {
		int[][] ans = null;
		/////// add your code below ///////
		ans = Arrays.copyOf(this._map, this._map.length); //deep copy
		///////////////////////////////////
		return ans;
	}
	@Override
	/////// add your code below ///////
	public int getWidth() {return this._map.length;}
	@Override
	/////// add your code below ///////
	public int getHeight() {return this._map[0].length;}
	@Override
	/////// add your code below ///////
	public int getPixel(int x, int y) {return this._map[x][y];}
	@Override
	/////// add your code below ///////
	public int getPixel(Pixel2D p) {
		return this.getPixel(p.getX(),p.getY()); //converts Pixel2D to X,Y
	}
	@Override
	/////// add your code below ///////
	public void setPixel(int x, int y, int v) {this._map[x][y] = v;}
	@Override
	/////// add your code below ///////
	public void setPixel(Pixel2D p, int v) {
		this.setPixel(p.getX(), p.getY(), v); //converts Pixel2D to X,Y
	}

	@Override
	/**
	 * Fills this map with the new color (new_v) starting from p.
	 * https://en.wikipedia.org/wiki/Flood_fill
	 */
	public int fill(Pixel2D xy, int new_v) {
		/*
		first, it checks that the color is already set because it will cause infinite loop.
		each time, it will paint itself and will paint its valid neighbors recursively
		 */
		int oldColor = getPixel(xy);
		int ans=0;

		if (getPixel(xy) != new_v) { //remove duplicates
			this.setPixel(xy, new_v);
			ans++;
			for (Pixel2D p: neighbors(xy, oldColor, true)) { //paint all valid neighbors
				ans += this.fill(p, new_v);
			}
		}
		return ans;
	}

	@Override
	/**
	 * BFS like shortest the computation based on iterative raster implementation of BFS, see:
	 * https://en.wikipedia.org/wiki/Breadth-first_search
	 */
	public Pixel2D[] shortestPath(Pixel2D p1, Pixel2D p2, int obsColor) {

		Pixel2D[] ans;  // the result.

		//get the distances from the start pixel using allDistances
		Map distanceMap = new Map(allDistance(p1, obsColor).getMap());

		//if there is no path between the two points, return null
		if (distanceMap.getPixel(p2) == -1) { //allDistances sets all blocked pixels as obstacles
			return null;
		}

		//set the length of ans
		int iteration = distanceMap.getPixel(p2)-1;

		if (iteration <= -1) { //there is no path
			return null;
		}

		ans = new Pixel2D[iteration+1];
		ans[iteration] = p2;
		distanceMap.setPixel(p2, -1);

		Index2D currentPixel = new Index2D(p2);

		//trace back the path
		for (;iteration > 0; iteration --) {
			/*
			iterate over all the valid neighbors, until finding the one with the right distance.
			then the neighbor is added to answer and repeats.
			*/
			for (Pixel2D neighbor :distanceMap.neighbors(currentPixel, -1, false)) {
				if (distanceMap.getPixel(neighbor) == iteration) {
					currentPixel = new Index2D(neighbor);
					break;
				}
			}

			ans[iteration - 1] = currentPixel;
		}

		return ans;
	}
	@Override
	/////// add your code below ///////
	public boolean isInside(Pixel2D p) {
		//checks if the X, Y of the point are lower than the width and height and not negative
		return (
				p.getX() < this.getWidth() && p.getY() < this.getHeight() &&
						p.getX() >= 0 && p.getY() >= 0
		);
	}

	@Override
	/////// add your code below ///////
	public boolean isCyclic() {
		return this._cyclicFlag;
	}
	@Override
	/////// add your code below ///////
	public void setCyclic(boolean cy) {
		this._cyclicFlag = cy;
	}
	@Override
	/////// add your code below ///////
	public Map2D allDistance(Pixel2D start, int obsColor) {

		//creates a new map and sets the start and the obstacles
		Map ans = new Map(getWidth(), getHeight(), -2);
		ans.setCyclic(isCyclic());
		ans.setPixel(start, 0);

		for (int x = 0; x < getWidth(); x++) {
			for (int y = 0; y < getHeight(); y++) {
				if (getPixel(x, y) == obsColor) {
					ans.setPixel(x, y, -1);
				}
			}
		}

		int iteration = 0;

		//the function will stop if no pixels got updated in an iteration
		boolean pixelsChanged = true;
		while (pixelsChanged) {
			pixelsChanged = false;

			//iterate over all the pixels
			for (int x = 0; x < getWidth(); x++) {
				for (int y = 0; y < getHeight(); y++) {

					if (ans.getPixel(x,y) == iteration) {
						//if the pixel is in the current iteration, change its neighbors

						for (Pixel2D p: ans.neighbors(new Index2D(x,y), -2, true)) {
							ans.setPixel(p, iteration + 1);
							pixelsChanged = true;
						}
					}
				}
			}
			iteration++;
		}

		//if a pixel is not reached, set it as an obstacle
		for (int x = 0; x < getWidth(); x++) {
			for (int y = 0; y < getHeight(); y++) {
				if (ans.getPixel(x, y) == -2) {
					ans.setPixel(x, y, -1);
				}
			}
		}
		return ans;
	}

	////////////private functions/////////////////
	private Pixel2D[] neighbors(Pixel2D currentPixel, int color, boolean same) {
		/*
		find all the neighbors of an index.
		this function also checks that the neighbors have the same color / are not an obstacle.
		returns an Index2D list
		 */

		Object[] changePoints = new Index2D[4];
		int ansLength = 0; //the number of valid neighbors


		changePoints[0] = new Index2D(currentPixel.getX() - 1, currentPixel.getY());
		changePoints[1] = new Index2D(currentPixel.getX() + 1, currentPixel.getY());
		changePoints[2] = new Index2D(currentPixel.getX(), currentPixel.getY() + 1);
		changePoints[3] = new Index2D(currentPixel.getX(), currentPixel.getY() - 1);

		for (int p = 0; p < changePoints.length; p++) {
			if (!isCyclic()) { //check if point is in range
				if (isInside((Pixel2D) changePoints[p])) {
					//check if the pixel color is valid
					if ((getPixel((Pixel2D) changePoints[p]) == color && same) || (getPixel((Pixel2D) changePoints[p]) != color && !same)) {
						ansLength++;

					} else {changePoints[p] = null;}

				} else {changePoints[p] = null;}

			} else { //cyclic

				//find the position on cyclic map using floorMod: second answer - https://stackoverflow.com/questions/5385024/mod-in-java-produces-negative-numbers
				changePoints[p] = new Index2D(Math.floorMod(((Pixel2D) changePoints[p]).getX(), getWidth()), Math.floorMod(((Pixel2D) changePoints[p]).getY(), getHeight()));

				//check if the pixel color is valid
				if ((getPixel((Pixel2D) changePoints[p]) == color && same) || (getPixel((Pixel2D) changePoints[p]) != color && !same)) {
					ansLength++;
				} else {changePoints[p] = null;}
			}
		}

		//insert all the valid points into ans
		Pixel2D[] ans = new Index2D[ansLength];
		ansLength = 0;
		for (Object v: changePoints) {
			if (v != null) {
				ans[ansLength] = (Pixel2D) v;
				ansLength++;
			}
		}
		return ans;
	}
}
