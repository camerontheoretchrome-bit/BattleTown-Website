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
//
// Empty means "not set up yet": the Store and Stats pages show their
// coming-soon text instead.
window.BT_CONFIG = {
  serverAddress: "play.battletown.store",
  discordUrl: "https://discord.gg/TJ5wBJYCc",
  tebexWebstoreToken: "14jdk-5b8a5aab70ca290954d04f1a993ac6223d18a630",
  statsFeedUrl: "https://api.battletown.store"
};
