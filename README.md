# mindustry-publish

Jitpack is cringe and unreliable, let us build Mindustry ourselves.

## How does it work

Mindustry and Arc are built with a GitHub action.
Then, the resulting artifacts are uploaded to our S3 server (minio).
Finally, they are served by our maven server (reposilite) via the [mindustry](https://maven.xpdustry.com/#/mindustry) repository.

## How to use it

Simply make sure you have these repositories in your build script.

```gradle
// Groovy
repositories {
    mavenCentral()
    maven { url = uri("https://maven.xpdustry.com/mindustry") }
    maven { url = uri("https://www.jitpack.io") }
}
```

```kt
// Kotlin
repositories {
    mavenCentral()
    maven("https://maven.xpdustry.com/mindustry")
    maven("https://www.jitpack.io")
}
```
