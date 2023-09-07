# mindustry-publish

Jitpack is cringe and unreliable, let us build Mindustry ourselves.

## How does it work

Mindustry, Arc and Rhino are built with a GitHub action.
Then, the resulting artifacts are uploaded to our S3 server (minio).
Finally, they are served by our maven server (reposilite) via the [mindustry](https://maven.xpdustry.com/#/mindustry) repository.

## How to use it

The repository provide all necessary dependencies for compiling Mindustry plugins and mods. You just have replace jitpack with it.

```gradle
// Groovy
repositories {
    mavenCentral()
    maven { url = uri("https://maven.xpdustry.com/mindustry") }
}
```

```kt
// Kotlin
repositories {
    mavenCentral()
    maven("https://maven.xpdustry.com/mindustry")
}
```

> **Warning**
> 
> The Maven repository does not provide any other library rewritten by Anuke apart Rhino.
> Thus if you want to use [Anuken's steamworks4j](https://github.com/Anuken/steamworks4j), you will have to comeback to Jitpack.

## Supported versions

- V146
- V145
