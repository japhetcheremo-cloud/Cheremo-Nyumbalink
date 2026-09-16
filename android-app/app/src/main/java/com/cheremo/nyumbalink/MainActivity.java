package com.cheremo.nyumbalink;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.view.KeyEvent;
import android.view.View;
import android.webkit.CookieManager;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.core.content.FileProvider;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class MainActivity extends AppCompatActivity {

    private static final String BASE_URL = "https://cheremo-nyumbalink.vercel.app";
    private static final int FILE_CHOOSER_REQUEST_CODE = 100;
    private static final int CAMERA_PERMISSION_REQUEST = 200;
    private static final int STORAGE_PERMISSION_REQUEST = 201;

    private WebView webView;
    private SwipeRefreshLayout swipeRefreshLayout;
    private LinearLayout offlineLayout;
    private LinearLayout loadingLayout;

    private ValueCallback<Uri[]> filePathCallback;
    private Uri cameraImageUri;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webview);
        swipeRefreshLayout = findViewById(R.id.swipe_refresh);
        offlineLayout = findViewById(R.id.offline_layout);
        loadingLayout = findViewById(R.id.loading_layout);
        Button retryButton = findViewById(R.id.retry_button);

        setupWebView();

        swipeRefreshLayout.setColorSchemeResources(R.color.brand_blue, R.color.brand_gold);
        swipeRefreshLayout.setOnRefreshListener(() -> {
            if (isNetworkAvailable()) {
                webView.reload();
            } else {
                swipeRefreshLayout.setRefreshing(false);
                showOffline();
            }
        });

        retryButton.setOnClickListener(v -> {
            if (isNetworkAvailable()) {
                showLoading();
                webView.loadUrl(BASE_URL);
            } else {
                Toast.makeText(this, "Still no connection. Please check your internet.", Toast.LENGTH_SHORT).show();
            }
        });

        if (isNetworkAvailable()) {
            showLoading();
            webView.loadUrl(BASE_URL);
        } else {
            showOffline();
        }
    }

    @SuppressWarnings("deprecation")
    private void setupWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setSupportZoom(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);

        // Enable cookies
        CookieManager.getInstance().setAcceptCookie(true);
        CookieManager.getInstance().setAcceptThirdPartyCookies(webView, true);

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                String url = request.getUrl().toString();
                // Open external links in browser (social, Google, etc.)
                if (!url.startsWith(BASE_URL) && !url.startsWith("https://accounts.google.com")) {
                    if (url.startsWith("http") || url.startsWith("https")) {
                        Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                        startActivity(intent);
                        return true;
                    }
                }
                return false;
            }

            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                super.onPageStarted(view, url, favicon);
                showLoading();
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                hideLoading();
                swipeRefreshLayout.setRefreshing(false);
                CookieManager.getInstance().flush();
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) {
                    hideLoading();
                    swipeRefreshLayout.setRefreshing(false);
                    showOffline();
                }
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> filePathCallback,
                                              FileChooserParams fileChooserParams) {
                MainActivity.this.filePathCallback = filePathCallback;
                openFileChooser();
                return true;
            }
        });
    }

    private void openFileChooser() {
        // Check permissions first
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_MEDIA_IMAGES)
                    != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this,
                        new String[]{Manifest.permission.READ_MEDIA_IMAGES, Manifest.permission.CAMERA},
                        CAMERA_PERMISSION_REQUEST);
                return;
            }
        } else {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_EXTERNAL_STORAGE)
                    != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this,
                        new String[]{Manifest.permission.READ_EXTERNAL_STORAGE, Manifest.permission.CAMERA},
                        STORAGE_PERMISSION_REQUEST);
                return;
            }
        }
        launchFileChooserIntent();
    }

    private void launchFileChooserIntent() {
        // Gallery intent
        Intent galleryIntent = new Intent(Intent.ACTION_GET_CONTENT);
        galleryIntent.setType("image/*");
        galleryIntent.addCategory(Intent.CATEGORY_OPENABLE);

        // Camera intent
        Intent cameraIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        try {
            File photoFile = createImageFile();
            cameraImageUri = FileProvider.getUriForFile(this,
                    getApplicationContext().getPackageName() + ".fileprovider", photoFile);
            cameraIntent.putExtra(MediaStore.EXTRA_OUTPUT, cameraImageUri);
        } catch (IOException e) {
            cameraImageUri = null;
        }

        Intent chooserIntent = Intent.createChooser(galleryIntent, "Select Image");
        chooserIntent.putExtra(Intent.EXTRA_INITIAL_INTENTS,
                new Intent[]{cameraIntent});

        startActivityForResult(chooserIntent, FILE_CHOOSER_REQUEST_CODE);
    }

    private File createImageFile() throws IOException {
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(new Date());
        String imageFileName = "CHEREMO_" + timeStamp + "_";
        File storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES);
        return File.createTempFile(imageFileName, ".jpg", storageDir);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == FILE_CHOOSER_REQUEST_CODE) {
            if (filePathCallback == null) return;
            Uri[] results = null;
            if (resultCode == RESULT_OK) {
                if (data != null && data.getData() != null) {
                    results = new Uri[]{data.getData()};
                } else if (cameraImageUri != null) {
                    results = new Uri[]{cameraImageUri};
                }
            }
            filePathCallback.onReceiveValue(results);
            filePathCallback = null;
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions,
                                           @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == CAMERA_PERMISSION_REQUEST || requestCode == STORAGE_PERMISSION_REQUEST) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                launchFileChooserIntent();
            } else {
                if (filePathCallback != null) {
                    filePathCallback.onReceiveValue(null);
                    filePathCallback = null;
                }
                Toast.makeText(this, "Permission denied. Cannot upload files.", Toast.LENGTH_SHORT).show();
            }
        }
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK && webView.canGoBack()) {
            webView.goBack();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }

    private boolean isNetworkAvailable() {
        ConnectivityManager cm = (ConnectivityManager) getSystemService(CONNECTIVITY_SERVICE);
        if (cm == null) return false;
        NetworkInfo activeNetwork = cm.getActiveNetworkInfo();
        return activeNetwork != null && activeNetwork.isConnected();
    }

    private void showLoading() {
        runOnUiThread(() -> {
            loadingLayout.setVisibility(View.VISIBLE);
            offlineLayout.setVisibility(View.GONE);
            webView.setVisibility(View.VISIBLE);
        });
    }

    private void hideLoading() {
        runOnUiThread(() -> {
            loadingLayout.setVisibility(View.GONE);
            offlineLayout.setVisibility(View.GONE);
            webView.setVisibility(View.VISIBLE);
        });
    }

    private void showOffline() {
        runOnUiThread(() -> {
            loadingLayout.setVisibility(View.GONE);
            offlineLayout.setVisibility(View.VISIBLE);
            webView.setVisibility(View.GONE);
        });
    }

    @Override
    protected void onPause() {
        super.onPause();
        webView.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        webView.onResume();
        if (!isNetworkAvailable()) {
            showOffline();
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        webView.destroy();
    }
}
