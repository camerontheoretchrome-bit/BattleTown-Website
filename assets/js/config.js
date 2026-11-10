// BattleTown website settings for the later phases.
//
// Everything here is PUBLIC: anyone can read this file in their browser.
// Never put a secret key, password or private token in it.
//
//   tebexWebstoreToken  Phase 2. The Tebex Headless *public* webstore
//                       token (Tebex panel > Integrations > Webstore token).
//                       It is meant to be public. The private key is not
//                       and must never go here.
//   statsFeedUrl        Phase 3. The HTTPS address of the plugin's
//                       read-only JSON stats feed, for example
//                       "https://api.battletown.store/stats.json".
//   alphaStart          When the whitelist comes off. Before it, the
//                       site says "invite-only" instead of "offline".
//                       Keep it equal to ALPHA_START in generate-pages.py.
//
// Empty means "not set up yet": the Store and Stats pages show their
// coming-soon text instead.
window.BT_CONFIG = {
  serverAddress: "play.battletown.store",
  discordUrl: "https://discord.gg/trSB8HCrTM",
  tebexWebstoreToken: "14jdk-5b8a5aab70ca290954d04f1a993ac6223d18a630",
  statsFeedUrl: "https://api.battletown.store",
  alphaStart: "2026-12-01T00:00:00-05:00"
};
