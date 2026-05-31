# Configuration

All configuration is read from environment variables. For local use they can be placed
in a `.env` file in the project root (auto-loaded), or supplied via the MCP client's
`env` block. Real environment variables always take precedence over `.env`.

## Variables

### Connection

- **`SYNOLOGY_URL`** *(required)* — base URL of the NAS, e.g. `http://192.168.1.100:5000`
  or `https://192.168.1.100:5001`. No trailing slash needed.
- **`SYNOLOGY_USER`** *(required)* — DSM username.
- **`SYNOLOGY_PASS`** *(required)* — DSM password.

### Two-factor authentication

- **`SYNOLOGY_DEVICE_ID`** — a persistent trusted-device token. Obtain it once with
  `python bootstrap_2fa.py <OTP>`; it is written to `.env` for you. With it set, the
  server logs in without an OTP.
- **`SYNOLOGY_OTP`** — a single OTP code. Only useful for the one-time bootstrap; it
  expires within 30 seconds and should not be relied on for normal operation.

### Behaviour

- **`SYNOLOGY_VERIFY_SSL`** *(default `false`)* — verify the TLS certificate. Set to
  `true` only if your NAS presents a valid (non-self-signed) certificate.
- **`SYNOLOGY_TIMEOUT`** *(default `30`)* — HTTP request timeout in seconds.
- **`SYNOLOGY_SESSION_NAME`** *(default `SynologyMCP`)* — session label shown in DSM.
- **`SYNOLOGY_DEVICE_NAME`** *(default `SynologyMCP`)* — device label shown in DSM's
  trusted-device list.

### Power control

- **`SYNOLOGY_ENABLE_POWER_CONTROL`** *(default `false`)* — when `true`, enables the
  destructive tools `reboot_nas`, `shutdown_nas` and `install_dsm_update`. They raise an
  error while disabled.

## Required privileges

Some tools need an account in the **administrators** group: storage/disk/pool info,
users/groups, shared-folder create/delete, security and certificate info, services,
hardware and power control. Read-only file and app tools generally work for normal users
with the relevant permissions. If a tool returns error **105**, the account lacks the
required privilege.

## Choosing a dedicated account

For least privilege, create a DSM user specifically for the server and grant only the
applications and shared folders it needs. Avoid using the built-in `admin` account.
