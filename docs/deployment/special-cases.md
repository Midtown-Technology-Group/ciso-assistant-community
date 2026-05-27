---
title: "Special cases"
description: "Tips and tricks regarding specific cases"
editUrl: "https://github.com/Midtown-Technology-Group/ciso-assistant-community/edit/docs/docs/deployment/special-cases.md"
---
# Special cases



### SELINUX

If you have selinux enabled on your distro, you might want to check if it's not preventing the mount volume of the docker compose; you can try something like this:

```
chcon -Rt svirt_sandbox_file_t ./db
```

