//ID:217280973
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;


public class Index2DTest {
    private static final double EPS = 0.01;
    Index2D p1 = new Index2D(2, 5);
    Index2D p2 = new Index2D(7, 5);
    Index2D p3 = new Index2D(2, 1);
    Index2D p4 = new Index2D(0, 0);

    Index2D p5 = new Index2D(-1, 1);
    @Test
    void testInit() {
        /*
        check if all types of initiators work,
         */
        Index2D p41 = new Index2D();//empty init
        assertEquals(p4.getX(), p41.getX());
        assertEquals(p4.getY(), p41.getY());

        Index2D p11 = new Index2D(p1); //duplicate init
        assertEquals(p1.getX(), p11.getX());
        assertEquals(p1.getY(), p11.getY());


    }
    @Test
    void testDistance() {
        /*
        checks if distance is accurate of the X axis, Y axis, one index to another and flipped and to a known result
         */
        assertEquals(p1.distance2D(p2), 5); //X axis

        assertEquals(p1.distance2D(p3), 4); //Y axis

        assertEquals(p1.distance2D(p4), p4.distance2D(p1)); //to other and flipped

        assertEquals(p1.distance2D(p5), 5); //known result: √(3^2 + 4^2)=5
    }

    @Test void testString() {
        /*
        check if String is equal to known value
         */
        assertEquals(p1.toString(), "2,5");
        assertEquals(p4.toString(), "0,0");
        assertEquals(p5.toString(), "-1,1");

    }

    @Test void testEquals() {
        /*
        check if equals function return true for index to himself and return false for completely different points
         */
        assertTrue(p1.equals(p1)); //to himself
        assertTrue(p4.equals(new Index2D()));

        assertFalse(p2.equals(p3)); //completely different points


    }
}
