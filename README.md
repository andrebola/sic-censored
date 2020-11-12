

# Instructions
## find censored artists
```bash
./scrapers/freemuse.py --region "europe" --country "spain"
```

## generate spotify top playlist
requires [Spotify api auth](https://developer.spotify.com/documentation/general/guides/app-settings/)
```bash
./scrapers/spotify.py --playlist_name "test" --artist "rosalia"
```

## collect lyrics

```bash
python scrapers/musixmatch_scraper.py --artist "Marcel Khalifa"
```
