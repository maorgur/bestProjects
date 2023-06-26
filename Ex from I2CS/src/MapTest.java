//ID:217280973
import org.junit.jupiter.api.Test;

import java.util.Arrays;

import static org.junit.jupiter.api.Assertions.*;

public class MapTest {
    int[][] zeroArr = new int[3][3];
    Map m1 = new Map(6, 6, 5);
    Index2D in1 = new Index2D(2, 5);

    //map and indexes for checking the algorithm
    Index2D startIndex = new Index2D(0, 0);
    Index2D endIndex = new Index2D(3, 3);

    int[][] m2Arr = {
            {0, -1, 0, 0 , 0 , 0},
            {0, -1, 0, -1, -1, 0},
            {0, -1, 0, 0 , -1, 0},
            {0, -1, -1, 0, -1, 0},
            {0, -1, -1, -1, -1,0},
            {0, 0, 0, 0 , 0 , 0 },
    };
    Map m2 = new Map(m2Arr);

    int[][] m3Arr = {
            {0, 0, -1, 0, 0, 0},
            {0, -1, 0, -1, 0, 0},
            {0, 0, 0, 0, -1, 0},
            {-1, -1, -1, 0, 0, 0},
            {0, -1, -1, -1, -1, 0},
            {0, -1, 0, -1, 0, -1},
    };
    Map m3 = new Map(m3Arr);

    @Test
    void testInit() {
        /*
        checks if all types of initialization work.
        also checks that it fails to create an invalid map
         */
        Map m2 = new Map(3);
        Map m3 = new Map(3, 3, 0);
        Map m4 = new Map(zeroArr);

        // check if all maps equals
        assertArrayEquals(m2.getMap(), m3.getMap());
        assertArrayEquals(m3.getMap(), m4.getMap());

        //check if asserting default value works
        assertEquals(m1.getPixel(1, 3), 5);

        int[][] emptyArr = new int[0][0];
        //check if fails to create an empty array and ragged array
        assertThrows(RuntimeException.class, () -> {
            new Map(emptyArr);
        }); //syntax by chat GPT
        assertThrows(RuntimeException.class, () -> {
            new Map(null);
        });
    }

    @Test
    void testPixel() {
        /*
        tests getPixel and setPixel with x, y and with Index2D
         */
        Map m12 = new Map(m1.getMap()); //create a deep copy to not interfere with other tests

        m12.setPixel(1, 5, 3);
        m12.setPixel(in1, 1);

        assertEquals(m12.getPixel(1, 5), 3);
        assertEquals(m12.getPixel(in1), 1);
    }

    @Test
    void testAllDistance() {
        /*
        checks if the distance of allDistance is equal to a manually solved map
         */
        int[][] m2Ans = { //solved manually
                {0, -1, 18, 17, 16, 15},
                {1, -1, 19, -1, -1, 14},
                {2, -1, 20, 21, -1, 13},
                {3, -1, -1, 22, -1, 12},
                {4, -1, -1, -1, -1, 11},
                {5, 6, 7, 8, 9, 10},
        };
        int[][] m2AnsCyclic = { //solved manually
                {0, -1, 4, 3, 2, 1},
                {1, -1, 5, -1, -1, 2},
                {2, -1, 6, 7, -1, 3},
                {3, -1, -1, 8, -1, 4},
                {2, -1, -1, -1, -1, 3},
                {1, 2, 3, 4, 3, 2},
        };
        m2.setCyclic(false);
        Map ans = (Map) m2.allDistance(startIndex, -1);
        m2.setCyclic(true);
        Map ansCyclic = (Map) m2.allDistance(startIndex, -1);

        //check if equals
        assertArrayEquals(ans.getMap(), m2Ans);
        assertArrayEquals(ansCyclic.getMap(), m2AnsCyclic);
    }


    @Test
    void testShortestPath() {
        /*
        checks if the shortest path length is correct
        checks if the path is not on obstacles and do not step on the same pixels twice or more
         */
        m2.setCyclic(false);
        Pixel2D[] pixels = m2.shortestPath(startIndex, endIndex, -1);
        Map2D m2Ans = m2.allDistance(startIndex, -1);
        assertEquals(pixels.length,m2Ans.getPixel(endIndex)); //check the number of points

        //check that all the pixels are valid

        for (int pixel = 0; pixel < pixels.length; pixel ++) {
            //check the pixel is valid
            assertNotEquals(m2Ans.getPixel(pixels[pixel]), -1);

            //check that there are no duplicates
            if (pixel > 0) {
                Object[] subPixels = Arrays.copyOfRange(pixels, 0, pixel);

                //check if an array contains a value: https://www.digitalocean.com/community/tutorials/java-array-contains-value
                assertFalse(Arrays.asList(subPixels).contains(pixels[pixel]));
            }
        }



    }


    @Test
    void testFill() {
        /*
        checks if fill paints all the pixels that allDistance shows as accessible
         */
        Index2D m3Start = new Index2D(3,3);

        //create a distance map
        m3.setCyclic(false);
        Map m3Ans = (Map) m3.allDistance(m3Start, -1);

        m3.setCyclic(true);
        Map m3AnsCyclic = (Map) m3.allDistance(m3Start, -1);

        //replace all non-obstacles values with 2 in answers
        for (int x = 0; x < m3.getWidth(); x++) {
            for (int y = 0; y < m3.getHeight(); y++) {
                if (m3Ans.getPixel(x,y) != -1) {m3Ans.setPixel(x,y,2);}
                if (m3AnsCyclic.getPixel(x,y) != -1) {m3AnsCyclic.setPixel(x,y,2);}
            }
        }
        //run fill and compare
        Map m3Fill = new Map(m3Arr);
        m3Fill.setCyclic(false);
        m3Fill.fill(m3Start, 2);

        int[][] m3Arr = { //reinitialize m3
                {0, 0, -1, 0, 0, 0},
                {0, -1, 0, -1, 0, 0},
                {0, 0, 0, 0, -1, 0},
                {-1, -1, -1, 0, 0, 0},
                {0, -1, -1, -1, -1, 0},
                {0, -1, 0, -1, 0, -1},
        };
        Map m3FillCyclic = new Map(m3Arr);
        m3FillCyclic.setCyclic(true);
        m3FillCyclic.fill(m3Start, 2);

        //in distance, all the inaccessible values are set to -1; the following code gets the same effect on fill
        for (int x = 0; x < m3.getWidth(); x++) {
            for (int y = 0; y < m3.getHeight(); y++) {
                if (m3Fill.getPixel(x,y) == 0) {m3Fill.setPixel(x,y,-1);}
                if (m3FillCyclic.getPixel(x,y) == 0) {m3FillCyclic.setPixel(x,y,-1);}
            }
        }

        assertTrue(Arrays.deepEquals(m3Fill.getMap(), m3Ans.getMap()));
        assertTrue(Arrays.deepEquals(m3FillCyclic.getMap(), m3AnsCyclic.getMap()));





    }
}