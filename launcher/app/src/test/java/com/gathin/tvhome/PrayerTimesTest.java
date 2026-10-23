package com.gathin.tvhome;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

import java.time.LocalDate;
import java.time.ZoneId;

/** Umm al-Qura times computed on the device (Qatar4u fork), checked against published Doha times. */
public class PrayerTimesTest {

    private static final ZoneId QATAR = ZoneId.of("Asia/Qatar");

    private static int min(int h, int m) {
        return h * 60 + m;
    }

    private static void near(String what, int expected, int actual) {
        assertTrue(what + ": expected about " + PrayerTimes.clock(expected) + ", got " + PrayerTimes.clock(actual),
                Math.abs(expected - actual) <= 3);
    }

    @Test
    public void dohaInOctober() {
        int[] t = PrayerTimes.minutes(LocalDate.of(2026, 10, 23), 25.2854, 51.5310, QATAR);
        near("Fajr", min(4, 17), t[0]);
        near("Sunrise", min(5, 35), t[1]);
        near("Dhuhr", min(11, 18), t[2]);
        near("Asr", min(14, 35), t[3]);
        near("Maghrib", min(17, 0), t[4]);
    }

    @Test
    public void ishaIsNinetyMinutesAfterMaghribOutsideRamadan() {
        int[] t = PrayerTimes.minutes(LocalDate.of(2026, 10, 23), 25.4250, 50.7850, QATAR);
        assertEquals(90, t[5] - t[4]);
    }

    @Test
    public void dukhanIsAFewMinutesAfterDoha() {
        LocalDate day = LocalDate.of(2026, 10, 23);
        int[] doha = PrayerTimes.minutes(day, 25.2854, 51.5310, QATAR);
        int[] dukhan = PrayerTimes.minutes(day, 25.4250, 50.7850, QATAR);
        for (int i = 0; i < 5; i++) {
            int d = dukhan[i] - doha[i];
            assertTrue("prayer " + i + " differs by " + d, d >= 1 && d <= 5);
        }
    }

    @Test
    public void timesAreInOrder() {
        for (int month = 1; month <= 12; month++) {
            int[] t = PrayerTimes.minutes(LocalDate.of(2027, month, 15), 25.4250, 50.7850, QATAR);
            for (int i = 1; i < t.length; i++) assertTrue("month " + month, t[i] > t[i - 1]);
        }
    }

    @Test
    public void nextSkipsSunriseAndWrapsToFajr() {
        int[] t = {min(4, 20), min(5, 39), min(11, 21), min(14, 37), min(17, 3), min(18, 33)};
        assertEquals(0, PrayerTimes.next(t, min(1, 0)));
        assertEquals(2, PrayerTimes.next(t, min(4, 30)));   // after Fajr: Dhuhr, not sunrise
        assertEquals(5, PrayerTimes.next(t, min(18, 0)));
        assertEquals(0, PrayerTimes.next(t, min(23, 0)));   // after Isha: tomorrow's Fajr
    }

    @Test
    public void clockIsTwelveHour() {
        assertEquals("4:05", PrayerTimes.clock(min(4, 5)));
        assertEquals("12:00", PrayerTimes.clock(min(12, 0)));
        assertEquals("6:33", PrayerTimes.clock(min(18, 33)));
    }

    @Test
    public void weatherCodesHaveArabicNames() {
        assertEquals("صافٍ", InfoPanel.describe(0));
        assertEquals("مطر", InfoPanel.describe(63));
        assertEquals("عاصفة رعدية", InfoPanel.describe(95));
    }
}
