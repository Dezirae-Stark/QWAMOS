# QWAMOS Docker Build System

Docker-based build and development environment for QWAMOS.

## Quick Start

### Build QWAMOS

```bash
# Build Docker images and compile QWAMOS
./docker/scripts/build.sh
```

### Run Tests

```bash
# Run full test suite in Docker
./docker/scripts/test.sh
```

### Development Container

```bash
# Start development environment
docker-compose -f docker/docker-compose.yml up -d qdev

# Access development container
docker exec -it qwamos-dev /bin/bash

# Stop development environment
docker-compose -f docker/docker-compose.yml down
```

## Docker Images

### qwamos/build (Production Build)
- **Base**: Debian stable-slim
- **Purpose**: Production builds and CI/CD
- **Includes**:
  - Python 3 + pip
  - Kotlin 1.9.20
  - Flutter 3.16.0
  - Android SDK + NDK
  - QEMU (x86, ARM)
  - liboqs (Post-Quantum Crypto)
  - Gradle 8.5
  - JDK 17

### qwamos/dev (Development)
- **Base**: Debian stable-slim
- **Purpose**: Interactive development
- **Includes**: Everything from build image plus:
  - LSP servers (Python, Kotlin, Bash, YAML)
  - Debuggers (gdb, lldb, strace, valgrind)
  - Development tools (vim, neovim, tmux, htop)
  - Android tools (adb, fastboot)
  - Documentation tools (Sphinx, MkDocs)
  - Node.js + npm

## Services

### qbuild
- **Image**: `qwamos/build:latest`
- **Purpose**: Production builds
- **Volumes**:
  - Repository (read-only)
  - Build artifacts output
  - Gradle/Flutter cache

### qdev
- **Image**: `qwamos/dev:latest`
- **Purpose**: Interactive development
- **Volumes**:
  - Repository (read-write)
  - Build artifacts
  - Caches (Gradle, Flutter, pip)
  - VSCode Remote Server
- **Ports**:
  - 8080, 8000, 5000, 3000 (web/API)
  - 5037 (ADB)

### qtest
- **Image**: `qwamos/build:latest`
- **Purpose**: Automated testing
- **Runs**: `docker/scripts/test.sh`

## Usage Examples

### Build Specific Module

```bash
# Access build container
docker exec -it qwamos-build /bin/bash

# Inside container
cd /workspace
python3 setup.py build
```

### Run VM Template Builds

```bash
docker exec qwamos-build bash vm-templates/scripts/build_qemu_template.sh
docker exec qwamos-build bash vm-templates/scripts/build_proot_template.sh
docker exec qwamos-build bash vm-templates/scripts/build_chroot_template.sh
```

### Run Specific Tests

```bash
# Python tests
docker exec qwamos-build pytest tests/ -v

# VM isolation tests
docker exec qwamos-build bash tests/vm-isolation/test_vm_isolation.sh

# Gateway tests
docker exec qwamos-build bash tests/gateway/test_gateway_security.sh

# PQC tests
docker exec qwamos-build python3 tests/pqc/test_pqc_security.py
```

### VSCode Remote Development

1. Install "Remote - Containers" extension
2. Open repository in VSCode
3. Command Palette → "Reopen in Container"
4. Select `qdev` service
5. VSCode connects to development container

### JetBrains Remote Development

1. Tools → Deployment → Configuration
2. Add Server → Docker Compose
3. Select `docker/docker-compose.yml`
4. Choose `qdev` service
5. Connect and code remotely

## Build Artifacts

Build artifacts are stored in `/build_artifacts` (inside container) and `./build_artifacts/` (on host).

**Artifacts Include**:
- Python packages (`.whl`, `.tar.gz`)
- VM templates (`.tar.gz`)
- Compiled binaries
- Test reports

## Cache Volumes

Persistent cache volumes speed up builds:
- `gradle-cache`: Gradle dependencies
- `flutter-cache`: Flutter SDK cache
- `pip-cache`: Python packages
- `vscode-server`: VSCode Remote Server

## GitHub Actions Integration

The workflow `.github/workflows/docker-build.yml` automatically:
1. Builds Docker images
2. Runs build script
3. Runs test script
4. Scans images for vulnerabilities (Trivy)
5. Uploads build artifacts

**Triggers**:
- Push to master
- Pull requests
- Manual dispatch

## Troubleshooting

### Build Failures

```bash
# View container logs
docker logs qwamos-build

# Access container for debugging
docker exec -it qwamos-build /bin/bash

# Rebuild without cache
docker build --no-cache -f docker/Dockerfile.build -t qwamos/build:latest .
```

### Permission Issues

```bash
# Fix ownership of build artifacts
sudo chown -R $USER:$USER build_artifacts/
```

### Clean Up

```bash
# Remove containers
docker-compose -f docker/docker-compose.yml down

# Remove volumes
docker-compose -f docker/docker-compose.yml down -v

# Remove images
docker rmi qwamos/build:latest qwamos/dev:latest

# Clean everything
docker system prune -a --volumes
```

## Environment Variables

**Build Container**:
- `QWAMOS_BUILD_ENV=docker`
- `PYTHONUNBUFFERED=1`
- `JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64`
- `ANDROID_HOME=/opt/android-sdk`
- `FLUTTER_HOME=/opt/flutter`
- `GRADLE_HOME=/opt/gradle`

**Development Container**:
- `QWAMOS_DEV_ENV=docker`
- `PYTHONUNBUFFERED=1`
- `DISPLAY=${DISPLAY:-:0}` (for GUI apps)

## Security Considerations

- Containers run as non-root user (`qwamos`)
- Build container mounts repository read-only
- Development container requires `privileged: true` for QEMU VM testing
- Security scanning via Trivy in CI/CD

## Performance Tips

1. **Use cache volumes**: Significantly speeds up repeated builds
2. **Layer caching**: Docker build cache reuses unchanged layers
3. **Parallel builds**: Use `docker-compose up` to run multiple services
4. **BuildKit**: Enable for faster builds (`DOCKER_BUILDKIT=1`)

## Contributing

When adding new dependencies:
1. Update appropriate Dockerfile (`Dockerfile.build` or `Dockerfile.dev`)
2. Rebuild images
3. Test build and development workflows
4. Update this README

## License

See [LICENSE](../LICENSE) file.
