package com.gathin.tvhome;

import android.icu.util.IslamicCalendar;
import android.icu.util.TimeZone;

import java.time.LocalDate;
import java.time.ZoneId;
import java.time.ZonedDateTime;

/**
 * Prayer times computed on the device, no network: Umm al-Qura method (Fajr 18.5 degrees, Isha 90 minutes
 * after Maghrib, 120 in Ramadan), Asr by the standard (Shafi'i) shadow ratio.
 * Sun position from the low-precision formulas of the US Naval Observatory, refined once at each time.
 */
final class PrayerTimes {

    static final String[] NAMES = {"الفجر", "الشروق", "الظهر", "العصر", "المغرب", "العشاء"};
    /** Index of the sunrise entry, which is shown but is not a prayer. */
    static final int SUNRISE = 1;

    private PrayerTimes() {}

    /** Today's six times (Fajr, Sunrise, Dhuhr, Asr, Maghrib, Isha) as minutes after local midnight. */
    static int[] minutes(LocalDate date, double lat, double lon, ZoneId zone) {
        double tz = zone.getRules().getOffset(date.atTime(12, 0)).getTotalSeconds() / 3600.0;
        double jd = julian(date) - lon / 360.0;
        // First guesses as day portions, then one refinement with the sun at each time.
        double[] t = {5, 6, 12, 13, 18, 18};
        for (int pass = 0; pass < 2; pass++) {
            double fajr = sunAngleTime(jd, t[0] / 24, 18.5, lat, true);
            double rise = sunAngleTime(jd, t[1] / 24, 0.833, lat, true);
            double noon = midDay(jd, t[2] / 24);
            double asr = asrTime(jd, t[3] / 24, lat);
            double set = sunAngleTime(jd, t[4] / 24, 0.833, lat, false);
            t = new double[] {fajr, rise, noon, asr, set, set};
        }
        int[] out = new int[6];
        for (int i = 0; i < 5; i++) {
            double h = t[i] + tz - lon / 15.0;
            out[i] = (int) Math.round(h * 60);
        }
        out[5] = out[4] + (isRamadan(date, zone) ? 120 : 90);
        return out;
    }

    /** Index of the next entry after {@code nowMin} that is a prayer (sunrise skipped), or 0 (tomorrow's Fajr). */
    static int next(int[] times, int nowMin) {
        for (int i = 0; i < times.length; i++) {
            if (i == SUNRISE) continue;
            if (times[i] > nowMin) return i;
        }
        return 0;
    }

    static String clock(int min) {
        min = ((min % 1440) + 1440) % 1440;
        int h = min / 60, m = min % 60;
        int h12 = h % 12 == 0 ? 12 : h % 12;
        return h12 + ":" + (m < 10 ? "0" : "") + m;
    }

    // ---- astronomy -----------------------------------------------------------------------------------

    private static double julian(LocalDate d) {
        int y = d.getYear(), m = d.getMonthValue(), day = d.getDayOfMonth();
        if (m <= 2) { y--; m += 12; }
        double a = Math.floor(y / 100.0);
        double b = 2 - a + Math.floor(a / 4);
        return Math.floor(365.25 * (y + 4716)) + Math.floor(30.6001 * (m + 1)) + day + b - 1524.5;
    }

    /** {declination in degrees, equation of time in hours} for a Julian day. */
    private static double[] sun(double jd) {
        double d = jd - 2451545.0;
        double g = fix(357.529 + 0.98560028 * d, 360);
        double q = fix(280.459 + 0.98564736 * d, 360);
        double l = fix(q + 1.915 * sin(g) + 0.020 * sin(2 * g), 360);
        double e = 23.439 - 0.00000036 * d;
        double ra = atan2(cos(e) * sin(l), cos(l)) / 15.0;
        ra = fix(ra, 24);
        double decl = asin(sin(e) * sin(l));
        double eqt = q / 15.0 - ra;
        return new double[] {decl, eqt};
    }

    private static double midDay(double jd, double portion) {
        double eqt = sun(jd + portion)[1];
        return fix(12 - eqt, 24);
    }

    private static double sunAngleTime(double jd, double portion, double angle, double lat, boolean ccw) {
        double decl = sun(jd + portion)[0];
        double noon = midDay(jd, portion);
        double t = acos((-sin(angle) - sin(decl) * sin(lat)) / (cos(decl) * cos(lat))) / 15.0;
        return noon + (ccw ? -t : t);
    }

    private static double asrTime(double jd, double portion, double lat) {
        double decl = sun(jd + portion)[0];
        double angle = -Math.toDegrees(Math.atan(1 / (1 + Math.tan(Math.toRadians(Math.abs(lat - decl))))));
        return sunAngleTime(jd, portion, angle, lat, false);
    }

    private static boolean isRamadan(LocalDate date, ZoneId zone) {
        try {
            IslamicCalendar cal = new IslamicCalendar(TimeZone.getTimeZone(zone.getId()));
            cal.setCalculationType(IslamicCalendar.CalculationType.ISLAMIC_UMALQURA);
            cal.setTimeInMillis(ZonedDateTime.of(date.atTime(12, 0), zone).toInstant().toEpochMilli());
            return cal.get(IslamicCalendar.MONTH) == IslamicCalendar.RAMADAN;
        } catch (RuntimeException e) {
            return false;
        }
    }

    /** Today's Umm al-Qura Hijri date in Arabic, e.g. "1 جمادى الأولى 1448 هـ". */
    static String hijri(LocalDate date, ZoneId zone) {
        try {
            IslamicCalendar cal = new IslamicCalendar(TimeZone.getTimeZone(zone.getId()));
            cal.setCalculationType(IslamicCalendar.CalculationType.ISLAMIC_UMALQURA);
            cal.setTimeInMillis(ZonedDateTime.of(date.atTime(12, 0), zone).toInstant().toEpochMilli());
            String[] months = {"محرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة",
                    "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"};
            return cal.get(IslamicCalendar.DAY_OF_MONTH) + " " + months[cal.get(IslamicCalendar.MONTH)]
                    + " " + cal.get(IslamicCalendar.YEAR) + " هـ";
        } catch (RuntimeException e) {
            return "";
        }
    }

    private static double fix(double a, double b) { a = a - b * Math.floor(a / b); return a < 0 ? a + b : a; }
    private static double sin(double d) { return Math.sin(Math.toRadians(d)); }
    private static double cos(double d) { return Math.cos(Math.toRadians(d)); }
    private static double asin(double x) { return Math.toDegrees(Math.asin(x)); }
    private static double acos(double x) { return Math.toDegrees(Math.acos(Math.max(-1, Math.min(1, x)))); }
    private static double atan2(double y, double x) { return Math.toDegrees(Math.atan2(y, x)); }
}
