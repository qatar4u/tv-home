package com.gathin.tvhome;

import android.content.Context;
import android.content.SharedPreferences;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Handler;
import android.os.Looper;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.TextView;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.ZoneId;

/**
 * Local fork addition (Qatar4u): today's prayer times, computed on the TV (Umm al-Qura), with the next prayer
 * highlighted, and the current weather from Open-Meteo (no key), refreshed every 30 minutes while Home is shown.
 * Off unless config.xml info_panel is true.
 */
final class InfoPanel {

    private static final long WEATHER_EVERY_MS = 30 * 60 * 1000L;
    private static final String PREFS = "info_panel";

    private final Context ctx;
    private final View panel;
    private final TextView weather;
    private final TextView hijri;
    private final TextView nextLine;
    private final TextView[] cells = new TextView[6];
    private final String city;
    private final double lat, lon;
    private final ZoneId zone = ZoneId.of("Asia/Qatar");
    private final Handler main = new Handler(Looper.getMainLooper());
    private volatile boolean fetching;
    private final float dp;

    InfoPanel(Context ctx, LinearLayout root, String city, double lat, double lon) {
        this.ctx = ctx;
        this.panel = root;
        this.city = city;
        this.lat = lat;
        this.lon = lon;
        dp = ctx.getResources().getDisplayMetrics().density;
        root.setVisibility(View.VISIBLE);
        // A dark frosted card, so the text stays readable over bright wallpapers.
        GradientDrawable card = new GradientDrawable();
        card.setColor(0x8C000000);
        card.setStroke((int) Math.max(1, dp), 0x26FFFFFF);
        card.setCornerRadius(18 * dp);
        root.setBackground(card);
        root.setPadding((int) (16 * dp), (int) (12 * dp), (int) (16 * dp), (int) (12 * dp));

        weather = text(17, 0xE6FFFFFF);
        root.addView(weather);

        hijri = text(13, 0x99FFFFFF);
        hijri.setPadding(0, (int) (4 * dp), 0, (int) (10 * dp));
        root.addView(hijri);

        LinearLayout prayerRow = new LinearLayout(ctx);
        prayerRow.setOrientation(LinearLayout.HORIZONTAL);
        LinearLayout.LayoutParams rowLp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        rowLp.gravity = Gravity.RIGHT;
        root.addView(prayerRow, rowLp);
        // Right to left, as Arabic reads: Fajr at the right edge, Isha at the left.
        for (int i = cells.length - 1; i >= 0; i--) {
            TextView c = text(14, 0x99FFFFFF);
            c.setGravity(Gravity.CENTER);
            c.setPadding((int) (12 * dp), (int) (6 * dp), (int) (12 * dp), (int) (6 * dp));
            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
            lp.setMarginStart((int) (6 * dp));
            prayerRow.addView(c, lp);
            cells[i] = c;
        }
        nextLine = text(13, 0xB3FFFFFF);
        nextLine.setPadding(0, (int) (8 * dp), (int) (4 * dp), 0);
        root.addView(nextLine);

        showCachedWeather();
    }

    private TextView text(int sp, int color) {
        TextView t = new TextView(ctx);
        t.setTextSize(TypedValue.COMPLEX_UNIT_SP, sp);
        t.setTextColor(color);
        t.setSingleLine(true);
        t.setIncludeFontPadding(false);
        t.setGravity(Gravity.RIGHT);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.gravity = Gravity.RIGHT;
        t.setLayoutParams(lp);
        return t;
    }

    /** Shown while the focus is on the dock row; faded out when the grid scrolls up over it. */
    void setShown(boolean shown) {
        float to = shown ? 1f : 0f;
        if (panel.getAlpha() == to) return;
        panel.animate().cancel();
        panel.animate().alpha(to).setDuration(shown ? 220 : 140).start();
    }

    /** Once a minute with the clock, and on every return to Home. */
    void update() {
        LocalDate today = LocalDate.now(zone);
        int now = LocalTime.now(zone).toSecondOfDay() / 60;
        int[] t = PrayerTimes.minutes(today, lat, lon, zone);
        int next = PrayerTimes.next(t, now);
        for (int i = 0; i < cells.length; i++) {
            cells[i].setText(PrayerTimes.NAMES[i] + "  " + PrayerTimes.clock(t[i]));
            boolean on = i == next;
            cells[i].setTextColor(on ? 0xFFFFFFFF : (i == PrayerTimes.SUNRISE ? 0x66FFFFFF : 0x99FFFFFF));
            cells[i].setTypeface(null, on ? Typeface.BOLD : Typeface.NORMAL);
            cells[i].setBackground(on ? glass() : null);
        }
        int target = t[next];
        if (target <= now) {   // after Isha: tomorrow's Fajr
            target = PrayerTimes.minutes(today.plusDays(1), lat, lon, zone)[0] + 1440;
        }
        int left = target - now;
        String in = left >= 60 ? (left / 60) + " س " + (left % 60) + " د" : left + " دقيقة";
        nextLine.setText("الصلاة القادمة: " + PrayerTimes.NAMES[next] + " بعد " + in);
        hijri.setText(PrayerTimes.hijri(today, zone));
        maybeFetchWeather();
    }

    private GradientDrawable glass() {
        GradientDrawable g = new GradientDrawable();
        g.setColor(0x33FFFFFF);
        g.setStroke((int) Math.max(1, dp), 0x4DFFFFFF);
        g.setCornerRadius(14 * dp);
        return g;
    }

    // ---- weather -------------------------------------------------------------------------------------

    private SharedPreferences prefs() { return ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE); }

    private void showCachedWeather() {
        String w = prefs().getString("text", null);
        weather.setText(w != null ? w : city + "  ·  الطقس قيد التحميل");
    }

    private void maybeFetchWeather() {
        long last = prefs().getLong("at", 0);
        if (fetching || System.currentTimeMillis() - last < WEATHER_EVERY_MS) return;
        fetching = true;
        new Thread(() -> {
            String line = null;
            try {
                line = fetch();
            } catch (Exception ignored) {
            }
            final String result = line;
            main.post(() -> {
                fetching = false;
                if (result != null) {
                    prefs().edit().putString("text", result).putLong("at", System.currentTimeMillis()).apply();
                    weather.setText(result);
                } else {
                    // Try again in 5 minutes, not every minute.
                    prefs().edit().putLong("at", System.currentTimeMillis() - WEATHER_EVERY_MS + 5 * 60 * 1000L).apply();
                }
            });
        }, "weather").start();
    }

    private String fetch() throws Exception {
        URL url = new URL("https://api.open-meteo.com/v1/forecast?latitude=" + lat + "&longitude=" + lon
                + "&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&timezone=Asia%2FQatar");
        HttpURLConnection c = (HttpURLConnection) url.openConnection();
        c.setConnectTimeout(8000);
        c.setReadTimeout(8000);
        try (InputStream in = c.getInputStream()) {
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            byte[] buf = new byte[4096];
            int n;
            while ((n = in.read(buf)) > 0 && out.size() < 64 * 1024) out.write(buf, 0, n);
            JSONObject cur = new JSONObject(out.toString("UTF-8")).getJSONObject("current");
            long temp = Math.round(cur.getDouble("temperature_2m"));
            int hum = (int) Math.round(cur.getDouble("relative_humidity_2m"));
            long wind = Math.round(cur.getDouble("wind_speed_10m"));
            String desc = describe(cur.getInt("weather_code"));
            return city + "  ·  " + temp + "°  " + desc + "  ·  رطوبة " + hum + "%  ·  رياح " + wind + " كم/س";
        } finally {
            c.disconnect();
        }
    }

    static String describe(int code) {
        if (code == 0) return "صافٍ";
        if (code == 1) return "صحو غالبًا";
        if (code == 2) return "غائم جزئيًا";
        if (code == 3) return "غائم";
        if (code == 45 || code == 48) return "ضباب";
        if (code >= 51 && code <= 57) return "رذاذ";
        if (code >= 61 && code <= 67) return "مطر";
        if (code >= 71 && code <= 77) return "ثلج";
        if (code >= 80 && code <= 82) return "زخات مطر";
        if (code >= 95) return "عاصفة رعدية";
        return "";
    }
}
