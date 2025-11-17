# Unity WebGL Export Workflow

Unity's WebGL export allows you to deploy Unity games directly to web browsers. This guide covers optimization, JavaScript interop, and best practices for web deployment.

## Table of Contents
- [WebGL Export Setup](#webgl-export-setup)
- [Optimization for Web](#optimization-for-web)
- [JavaScript Interop](#javascript-interop)
- [Claude Code Assistance](#claude-code-assistance)
- [Deployment Strategies](#deployment-strategies)

## WebGL Export Setup

### Build Settings

1. **Switch Platform to WebGL**
   - File → Build Settings → WebGL → Switch Platform
   - Wait for Unity to re-import assets

2. **Player Settings Configuration**

```
Edit → Project Settings → Player → WebGL Settings

Resolution and Presentation:
  - Default Canvas Width: 960
  - Default Canvas Height: 600
  - Run In Background: true

Rendering:
  - Color Space: Linear (better quality)
  - Auto Graphics API: true
  - Compression Format: Gzip or Brotli

Publishing Settings:
  - Compression Format: Gzip
  - Enable Exceptions: None (smaller build)
  - Data caching: true
  - Debug Symbols: false (production)

Memory:
  - Memory Size: 256 MB (adjust based on needs)
```

### Build Command Line

```bash
# Build from command line (useful for CI/CD)
/Applications/Unity/Hub/Editor/2021.3.0f1/Unity.app/Contents/MacOS/Unity \
  -quit \
  -batchmode \
  -projectPath /path/to/project \
  -buildTarget WebGL \
  -executeMethod BuildScript.PerformBuild

# BuildScript.cs
using UnityEditor;

public class BuildScript {
    public static void PerformBuild() {
        BuildPipeline.BuildPlayer(
            new[] { "Assets/Scenes/Game.unity" },
            "Build/WebGL",
            BuildTarget.WebGL,
            BuildOptions.None
        );
    }
}
```

## Optimization for Web

### Asset Optimization

#### 1. Texture Compression

```csharp
// TextureOptimizer.cs
using UnityEngine;
using UnityEditor;

public class TextureOptimizer {
    [MenuItem("Tools/Optimize Textures for WebGL")]
    static void OptimizeTextures() {
        string[] guids = AssetDatabase.FindAssets("t:Texture2D");

        foreach (string guid in guids) {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;

            if (importer != null) {
                // Set WebGL-specific settings
                var settings = importer.GetPlatformTextureSettings("WebGL");
                settings.overridden = true;
                settings.maxTextureSize = 2048;
                settings.format = TextureImporterFormat.DXT5Crunched;
                settings.compressionQuality = 50;

                importer.SetPlatformTextureSettings(settings);
                AssetDatabase.ImportAsset(path);
            }
        }

        Debug.Log("Texture optimization complete");
    }
}
```

#### 2. Audio Compression

```csharp
// Set in Inspector or via script
AudioImporter:
  - Load Type: Streaming (for music)
  - Load Type: Compressed In Memory (for SFX)
  - Compression Format: Vorbis
  - Quality: 50-70%
```

#### 3. Model Optimization

```
Models:
  - Read/Write Enabled: false
  - Optimize Mesh: true
  - Mesh Compression: High
  - Normal/Tangents: Calculate if needed, otherwise None
  - Blend Shapes: Remove if not used
  - Animation: Optimal compression
```

### Code Optimization

```csharp
// WebGLOptimizer.cs
using UnityEngine;

public class WebGLOptimizer : MonoBehaviour {
    void Start() {
        // Reduce quality on WebGL
        if (Application.platform == RuntimePlatform.WebGLPlayer) {
            QualitySettings.SetQualityLevel(2); // Medium quality
            Application.targetFrameRate = 60;

            // Disable expensive features
            QualitySettings.shadows = ShadowQuality.Disable;
            QualitySettings.shadowDistance = 0;
            QualitySettings.pixelLightCount = 1;

            // Adjust physics
            Physics.defaultSolverIterations = 4;
            Physics.defaultSolverVelocityIterations = 1;
        }
    }

    void Update() {
        // Monitor performance
        if (Time.frameCount % 60 == 0) {
            float fps = 1.0f / Time.deltaTime;
            if (fps < 30) {
                ReduceQuality();
            }
        }
    }

    void ReduceQuality() {
        // Dynamic quality adjustment
        QualitySettings.SetQualityLevel(
            Mathf.Max(0, QualitySettings.GetQualityLevel() - 1)
        );
    }
}
```

### Loading Screen

```csharp
// LoadingScreen.cs
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

public class LoadingScreen : MonoBehaviour {
    [SerializeField] private Slider progressBar;
    [SerializeField] private Text loadingText;

    void Start() {
        StartCoroutine(LoadGameScene());
    }

    IEnumerator LoadGameScene() {
        // Simulate asset loading
        yield return new WaitForSeconds(0.5f);

        AsyncOperation operation = SceneManager.LoadSceneAsync("Game");
        operation.allowSceneActivation = false;

        while (!operation.isDone) {
            float progress = Mathf.Clamp01(operation.progress / 0.9f);
            progressBar.value = progress;
            loadingText.text = $"Loading... {(progress * 100):F0}%";

            if (operation.progress >= 0.9f) {
                loadingText.text = "Press any key to continue";

                if (Input.anyKeyDown) {
                    operation.allowSceneActivation = true;
                }
            }

            yield return null;
        }
    }
}
```

## JavaScript Interop

### Unity → JavaScript Communication

```csharp
// UnityToJS.cs
using UnityEngine;
using System.Runtime.InteropServices;

public class UnityToJS : MonoBehaviour {
    // Import JavaScript functions
    [DllImport("__Internal")]
    private static extern void SendScoreToJS(int score);

    [DllImport("__Internal")]
    private static extern void OpenURL(string url);

    [DllImport("__Internal")]
    private static extern string GetPlayerName();

    public void OnGameOver(int score) {
        #if UNITY_WEBGL && !UNITY_EDITOR
        SendScoreToJS(score);
        #endif
    }

    public void OpenLeaderboard() {
        #if UNITY_WEBGL && !UNITY_EDITOR
        OpenURL("https://example.com/leaderboard");
        #endif
    }

    void Start() {
        #if UNITY_WEBGL && !UNITY_EDITOR
        string playerName = GetPlayerName();
        Debug.Log($"Player name from JS: {playerName}");
        #endif
    }
}
```

JavaScript plugin file (`Assets/Plugins/WebGL/MyPlugin.jslib`):

```javascript
mergeInto(LibraryManager.library, {
    SendScoreToJS: function(score) {
        // Send score to external JavaScript
        window.gameScore = score;

        // Call external API
        if (window.sendScoreToServer) {
            window.sendScoreToServer(score);
        }

        // Analytics
        if (window.gtag) {
            gtag('event', 'game_over', {
                'event_category': 'game',
                'value': score
            });
        }
    },

    OpenURL: function(urlPtr) {
        var url = UTF8ToString(urlPtr);
        window.open(url, '_blank');
    },

    GetPlayerName: function() {
        var name = window.playerName || 'Guest';
        var bufferSize = lengthBytesUTF8(name) + 1;
        var buffer = _malloc(bufferSize);
        stringToUTF8(name, buffer, bufferSize);
        return buffer;
    }
});
```

### JavaScript → Unity Communication

HTML integration:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Unity WebGL Game</title>
    <style>
        body { margin: 0; padding: 0; overflow: hidden; }
        #unity-container { width: 100vw; height: 100vh; }
        #unity-canvas { width: 100%; height: 100%; }
        #loading-screen {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: #000;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
    </style>
</head>
<body>
    <div id="unity-container">
        <canvas id="unity-canvas"></canvas>
        <div id="loading-screen">Loading...</div>
    </div>

    <script src="Build/Build.loader.js"></script>
    <script>
        var unityInstance;

        // Configuration
        var buildUrl = "Build";
        var loaderUrl = buildUrl + "/Build.loader.js";
        var config = {
            dataUrl: buildUrl + "/Build.data",
            frameworkUrl: buildUrl + "/Build.framework.js",
            codeUrl: buildUrl + "/Build.wasm",
            streamingAssetsUrl: "StreamingAssets",
            companyName: "MyCompany",
            productName: "MyGame",
            productVersion: "1.0",
        };

        // Loading progress
        var loadingScreen = document.getElementById('loading-screen');

        createUnityInstance(document.getElementById("unity-canvas"), config, (progress) => {
            loadingScreen.textContent = `Loading... ${Math.round(progress * 100)}%`;
        }).then((instance) => {
            unityInstance = instance;
            loadingScreen.style.display = 'none';
            console.log('Unity loaded successfully');

            // JavaScript → Unity communication examples
            window.startGame = function() {
                unityInstance.SendMessage('GameManager', 'StartGame');
            };

            window.setDifficulty = function(level) {
                unityInstance.SendMessage('GameManager', 'SetDifficulty', level);
            };

            window.pauseGame = function() {
                unityInstance.SendMessage('GameManager', 'PauseGame');
            };

            // External API example
            window.sendScoreToServer = async function(score) {
                try {
                    const response = await fetch('/api/scores', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ score })
                    });
                    const data = await response.json();
                    console.log('Score submitted:', data);
                } catch (error) {
                    console.error('Failed to submit score:', error);
                }
            };

        }).catch((message) => {
            alert('Failed to load Unity: ' + message);
        });

        // Fullscreen API
        function enterFullscreen() {
            if (unityInstance) {
                unityInstance.SetFullscreen(1);
            }
        }

        // Mobile optimization
        if (/iPhone|iPad|iPod|Android/i.test(navigator.userAgent)) {
            config.devicePixelRatio = 1;
            document.getElementById('unity-canvas').style.width = "100%";
            document.getElementById('unity-canvas').style.height = "100%";
        }
    </script>
</body>
</html>
```

### Unity Component for JS Communication

```csharp
// GameManager.cs
using UnityEngine;

public class GameManager : MonoBehaviour {
    private static GameManager instance;

    void Awake() {
        if (instance == null) {
            instance = this;
            DontDestroyOnLoad(gameObject);
        }
    }

    // Called from JavaScript
    public void StartGame() {
        Debug.Log("Starting game from JavaScript");
        // Load game scene
        UnityEngine.SceneManagement.SceneManager.LoadScene("Game");
    }

    public void SetDifficulty(string level) {
        Debug.Log($"Setting difficulty to: {level}");
        // Apply difficulty settings
    }

    public void PauseGame() {
        Time.timeScale = Time.timeScale == 0 ? 1 : 0;
    }

    // Call JavaScript from Unity
    public void NotifyJavaScript(string message) {
        #if UNITY_WEBGL && !UNITY_EDITOR
        Application.ExternalCall("unityCallback", message);
        #endif
    }
}
```

## Claude Code Assistance

### Optimization Prompts

```
Analyze my Unity WebGL build size and suggest optimizations
```

```
Create a loading screen for Unity WebGL with progress bar
```

```
Optimize my Unity game textures for WebGL deployment
```

```
Implement JavaScript interop for Unity WebGL analytics
```

### Integration Prompts

```
Create a Unity WebGL wrapper with responsive design
```

```
Implement mobile touch controls for Unity WebGL game
```

```
Add external leaderboard integration to Unity WebGL
```

```
Create a payment integration for Unity WebGL game
```

## Deployment Strategies

### Hosting Options

#### 1. GitHub Pages

```bash
# Build Unity to Build/WebGL folder
# Create .nojekyll file to prevent Jekyll processing
touch Build/WebGL/.nojekyll

# Push to gh-pages branch
git subtree push --prefix Build/WebGL origin gh-pages
```

#### 2. Netlify

```toml
# netlify.toml
[build]
  publish = "Build/WebGL"
  command = "echo 'Unity build already complete'"

[[headers]]
  for = "/*"
  [headers.values]
    Access-Control-Allow-Origin = "*"

[[headers]]
  for = "*.wasm"
  [headers.values]
    Content-Type = "application/wasm"

[[headers]]
  for = "*.data"
  [headers.values]
    Content-Type = "application/octet-stream"

[[headers]]
  for = "*.framework.js"
  [headers.values]
    Content-Type = "application/javascript"
```

#### 3. Cloudflare Pages

```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloudflare Pages

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Publish to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: my-unity-game
          directory: Build/WebGL
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}
```

### Compression

```nginx
# nginx.conf for optimal Unity WebGL serving
server {
    listen 80;
    server_name yourgame.com;

    location / {
        root /var/www/unity-game;
        index index.html;

        # Enable gzip
        gzip on;
        gzip_types application/javascript application/wasm application/octet-stream;
        gzip_vary on;

        # Brotli (if available)
        brotli on;
        brotli_types application/javascript application/wasm application/octet-stream;

        # CORS headers
        add_header Access-Control-Allow-Origin *;

        # Cache control
        location ~* \.(data|wasm)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        location ~* \.(js)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

### Performance Monitoring

```html
<script>
    // Monitor Unity performance
    createUnityInstance(canvas, config, (progress) => {
        // Track loading progress
        if (window.gtag) {
            gtag('event', 'unity_loading', {
                'event_category': 'performance',
                'value': Math.round(progress * 100)
            });
        }
    }).then((instance) => {
        // Track successful load
        const loadTime = performance.now();
        if (window.gtag) {
            gtag('event', 'unity_loaded', {
                'event_category': 'performance',
                'value': Math.round(loadTime)
            });
        }

        // Monitor FPS
        let frameCount = 0;
        let lastTime = performance.now();

        setInterval(() => {
            const currentTime = performance.now();
            const fps = (frameCount / (currentTime - lastTime)) * 1000;

            if (fps < 30) {
                console.warn('Low FPS detected:', fps);
            }

            frameCount = 0;
            lastTime = currentTime;
        }, 1000);

        requestAnimationFrame(function countFrames() {
            frameCount++;
            requestAnimationFrame(countFrames);
        });
    });
</script>
```

## Best Practices

1. **Keep Build Size Small**: Target < 50 MB compressed
2. **Use Code Stripping**: Enable in Player Settings
3. **Asset Bundle Loading**: Load large assets asynchronously
4. **Mobile Testing**: Test on actual mobile devices, not just desktop browsers
5. **Memory Management**: Monitor heap size, avoid memory leaks
6. **Loading Screen**: Always show loading progress
7. **Error Handling**: Provide fallback for WebGL-unsupported browsers
8. **Analytics**: Track load times, FPS, errors

## Troubleshooting

### Build Size Too Large

- Enable code stripping
- Use asset bundles for large assets
- Compress textures and audio
- Remove unused assets

### Poor Performance

- Reduce draw calls
- Lower quality settings
- Optimize physics
- Use object pooling
- Reduce particle effects

### Loading Fails

- Check browser console for errors
- Verify CORS headers
- Check file paths
- Test on different browsers

## Next Steps

- Explore [Custom Engine Development](./custom-engine-development.md)
- Learn [Performance Optimization](../10-performance-optimization/README.md)
- Review [Deployment Guide](../12-deployment-distribution/README.md)
