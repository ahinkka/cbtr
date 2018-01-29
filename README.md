# Content Based Text Recommendation

This is the beginning of a context based text recommendation system proof of
concept.

Things to discover with this PoC:
- At least one working recommendation method.
- Very crude A/B testing implementation (between random and the method).
- Microserver architecture using Docker to simulate a somewhat realistic
  real-world system where not everything runs in the same application due to
  scaling concerns etc.


## How to build and run

Follow the instructions under `corpora/README.md`.

Then run `docker-compose build`.
