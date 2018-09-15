tunel
=====

**The out-of-the-box automated TLS termination reverse proxy for a docker environment.**


Features
--------
- TLS 1.2 termination,
- SNI based routing,
- Let's Encrypt's certificates issuance and renewal,
- Container labels based domain binding.


Quick start
-----------

To expose your web service container to the World,
simply set it's `domain` label to the domain name you want to assign to it:
`docker run ... -l domain=example.com ...` 

Run `tunel` instance, expose it's HTTP and HTTPS ports to the public and give it access to the host docker: 

    docker run \
        -p 80:80 \
        -p 443:443 \
        -v tunel:/var/ctx \
        -v /var/run/docker.sock:/var/run/docker.sock \
        majkrzak/tunel

That's it, now you can connect your's web service via https://example.com


Configuration
-------------

- `CONTEXT`    — directory where internal service state will be persisted.
                 _Defaults to `.` which is exposed as docker volume mount point._
- `DIRECTORY`  — url of ACME v2 compatible certificate authority directory.
                 _Defaults to `https://acme-v02.api.letsencrypt.org/directory`_
- `HTTP_PORT`  — HTTP redirect server listen port.
                 _Defaults to protocol default `80`_
- `HTTPS_PORT` — HTTPS reverse proxy server listen port.
                 _Defaults to protocol default `443`_


License
-------
Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.


References
----------

Github: https://github.com/majkrzak/tunel/

Docker hub: https://hub.docker.com/r/majkrzak/tunel
