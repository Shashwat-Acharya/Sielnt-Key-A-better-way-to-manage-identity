# Core Engine

This directory contains the cross-platform C++ secure engine for biometric processing and cryptographic operations.

## Overview

The core engine provides high-performance, security-critical functionality for:
- Biometric template extraction and matching
- Cryptographic operations
- Secure memory management
- Cross-platform compatibility

## Components

### Biometric Processing
- **biometric_template_parsing.cpp** - Biometric template extraction, parsing, and matching algorithms

## Technology Stack

- **Language**: C++
- **Build System**: CMake (planned)
- **Platforms**: Windows, Linux, macOS

## Security Considerations

This is a security-critical component. All code undergoes:
- Secure code reviews
- Memory safety audits
- Cryptographic validation
- Cross-platform testing

## Building

Build instructions are documented in the root CMakeLists.txt when fully set up.

## Integration

The core engine is used by:
- Desktop clients
- Mobile applications
- Web services via C++ bindings

## Related Documentation

- [Main README](../README.md)
- [Backend](../backend/)
- [Infrastructure](../infra/)
