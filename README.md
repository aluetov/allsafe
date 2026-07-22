### Known Limitations & Future Roadmap

* **Only A Records:** Currently, the scanner only queries `A` records. The architecture is designed to easily extend this to `MX`, `NS`, `TXT`, etc., in a future iteration.
* **No Caching:** Repeated queries for the same domain hit the upstream resolver every time. (Redis caching planned).
* **No Persistence:** Scan results are returned to the client but not saved. (Postgres database planned).

#### Resolved 
* ~~Blocking DNS calls (Switched to `dns.asyncresolver` to free the event loop)~~
* ~~No timeout on resolutions (Added `lifetime` boundary)~~
* ~~No input validation (Added Pydantic regex boundary)~~
* ~~Unpredictable host resolution (Pinned to `8.8.8.8` module-level resolver)~~