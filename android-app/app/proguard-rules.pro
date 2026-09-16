# Add project specific ProGuard rules here.
-keepattributes *Annotation*
-keep class com.cheremo.nyumbalink.** { *; }
-keepclassmembers class * extends android.webkit.WebViewClient {
    public *;
}
-keepclassmembers class * extends android.webkit.WebChromeClient {
    public *;
}
