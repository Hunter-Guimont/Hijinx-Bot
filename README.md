## Hijinx Future Development Plan
---
### Moderation Commands (Admin-only):

* __Role Management Commands__
  * `toprole <user>`: State the users top role.
  * `roles <user>`: List all of a user's current role(s).
  * `addrole <user> <role>`: Add addition role.
  * `removerole <user> <role>`: Remove existing role.
  * `perms <user>`: Display all permissions user does & does not have.
 
 
* __Ban / Mute Commands:__ 
  * `kick <user> <hours> [reason]`: Temp-ban a user temporarily.
  * `ban <user> [reason]`: Ban a specified user permanently.
  * `gag <user> <hours> [reason]`: Mute voice of user temporarily.
  * `mute <user> <hours> [reason]`: Remove text chat permissions temporarily.
 
 ---
### Auto-Mod, Auto-Role & Time-Roles: 

* __Auto-Mod Listeners (Toggleable)__
  * `spam`: Warn or Temporarily mute user if spamming detected.
  * `invites`: Automatically remove guild/bot invites where disallowed.
  * `links`: Automatically remove any and all links where disallowed.

---
### Database for guild/user personal options continuity

* __Store guild information such as:__
  * Each guilds's `guild.id` for identification.
  * Auto-Mod settings:
    * `spam <on|off>` Set whether filter should be active or not. 
    * `spamthreshold <low|medium|high>`
      * High: 10 messages in 30 seconds, or just 30 in row.
      * Medium: 10 messages in 20 second, or just 20 in a row.
      * Low: 10 messages in 10 seconds, or just 10 in a row.
    * `links <on|off>` 
* __Store user information such as:__
  * ... 

---
### Custom Help Command:

Possible non-embeded design for place holder or simply just ease of use :

    *`cogname`:*\
    *¶* `command1`  `<arg>`  `[kwarg]`: **This is what the command does.**\
    *¶* `command1`  `<arg>`  `[kwarg]`: **This is what the command does.**\
    *¶* `command3`  `<arg>`  `[kwarg]`: **This is what the command does.**\
    *¶* `command4`  `<arg>`  `[kwarg]`: **This is what the command does.**\

    *`cogname`:*\
    *¶* `command1`  `<arg>`  `[kwarg]`: **This is what the command does.**\
    *¶* `command1`  `<arg>`  `[kwarg]`: **This is what the command does.**\
    *¶* `command3`  `<arg>`  `[kwarg]`: **This is what the command does.**\
    *¶* `command4`  `<arg>`  `[kwarg]`: **This is what the command does.**\

