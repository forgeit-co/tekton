set shell := ["bash", "-cu"]

import 'just/quality.just'
import 'just/dev.just'
import 'just/operations.just'
import 'just/deploy.just'
import 'just/ports.just'

# List all project tasks.
default:
  @just --list
