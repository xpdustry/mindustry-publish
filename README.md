# mindustry-publish

[![Xpdustry latest](https://maven.xpdustry.com/api/badge/latest/mindustry/com/github/Anuken/Mindustry/core?color=008080&name=Mindustry)](https://maven.xpdustry.com/#/mindustry/com/github/Anuken/Mindustry/core)
[![Mindustry 7.0 | 8.0](https://img.shields.io/badge/Mindustry-7.0%7C8.0-008080)](https://github.com/Anuken/Mindustry/releases)

## Description

Jitpack is a great tool. It allows you to distribute your project without the need to setup publishing to maven central.
All you need to do is creating a very small yaml file in your project and Jitpack will build and publish for any tag or commit.

For Mindustry, it was great, until the git repository of Mindustry grew past 2GB. Jitpacks now always fails to process Mindustry.
Fortunatly, **mindustry-publish** solves this.

## How does it work ?

We simply compile Mindustry, Arc and Rhino ourselves with a Github Action, since they don't have tight restrictions like Jitpack.
Then the resulting jar artifacts are uploaded to our [S3 server](https://minio.xpdustry.com),
and served by our [maven repository](https://maven.xpdustry.com) via the [mindustry](https://maven.xpdustry.com/#/mindustry) repository.

## How to use it ?

Our maven repository provide all the necessary dependencies for compiling Mindustry mods and plugins.

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

That's it! And no need to modify your dependency declarations:

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

- v152.1
- v152
- v151.1
- v151
- v150.1
- v150
- v149
- v148
- v147
- v146
- v145
