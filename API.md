# Python Pathfinder API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [REST API Endpoints](#rest-api-endpoints)
   - [Users](#users)
   - [Game Progress](#game-progress)
   - [Multiplayer](#multiplayer)
   - [Leaderboards](#leaderboards)
   - [Challenges](#challenges)
4. [WebSocket Events](#websocket-events)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Examples](#examples)

## Overview

Python Pathfinder provides a RESTful API for managing game data, user accounts, and real-time multiplayer features. All API responses are in JSON format.

**Base URL:** `https://your-domain.com/api/v1/`

## Authentication

Most endpoints require authentication using session cookies (web) or JWT tokens (mobile).

### Session Authentication (Web)
- Uses Flask session cookies
- Automatically handled by browsers
- Requires `session['user_id']` to be set

### JWT Authentication (Mobile/API)