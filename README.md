# mindustry-publish

## Description

Jitpack is a nice tool to distribute jars without the need to setup a maven server.
But for Mindustry, it worked for a while. But due to the huge size of the Mindustry git repository, it now always fails spectacularely most of the time.
Fortunatly, **mindustry-publish** solves this.

## How it works ?

We compile Mindustry, Arc and Rhino with a GitHub action.
Then, the jar artifacts are uploaded to our [S3 server](https://minio.xpdustry.com).
And finally, they are served by our [maven server](https://maven.xpdustry.com) via the [mindustry](https://maven.xpdustry.com/#/mindustry) repository.

## How to use it ?

Our repository provide all necessary dependencies for compiling Mindustry plugins and mods.

Update your repository declaration block in your build script to look like this:

```groovy
// Groovy
repositories {
    mavenCentral()
    maven { url = uri("https://maven.xpdustry.com/mindustry") }
    // maven { url = uri("https://jitpack.io") }
}
```

```kt
// Kotlin
repositories {
    mavenCentral()
    maven("https://maven.xpdustry.com/mindustry")
    // maven("https://jitpack.io")
}
```

That's it! And no need to modify your dependencies declaration:

```groovy
// Groovy
dependencies {
    implementation "com.github.Anuken.Mindustry:core:v148"
    // implementation "com.github.Anuken.Mindustry:server:v148"
}
```

```kt
// Kotlin
dependencies {
    implementation("com.github.Anuken.Mindustry:core:v148")
    // implementation("com.github.Anuken.Mindustry:server:v148")
}
```

> **Warning**
> 
> The Maven repository does not provide any other library rewritten by Anuke apart Rhino.
> Thus if you want to use [Anuken's steamworks4j](https://github.com/Anuken/steamworks4j), you will have to comeback to Jitpack.

## Supported versions

- v148
- v147
- v146
- v145
