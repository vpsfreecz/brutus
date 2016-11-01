# The Website Module

## Introduction

The **website** module manages per-site Nginx configuration

## Configuration directives

#### catalog
> Syntax: `catalog: website`  

#### domain
> Syntax: `domain: `*`domain_name`*  
> Example: `domain: example.net`  
> References: [domain id][brutus_domain_id] 

#### id
> Syntax: `id: `*`website_id`*  
> Default: `id: `**`$domain`**  
> Example: `id: example.net`  

#### name
> Syntax: `name: `*`server_name`*  
> Default: `name: `**`$id`**  
> Example: `name: example.net`  

Specifies which requests are served using this configuration.
Corresponds to nginx [`server_name`][ngx_server_name] directive.

#### root
> Syntax: `root: `*`path`*  
> Default: `root: /srv/www/`**`$domain`**`/`**`$id`**`/www`  
> Example: `root: /var/www/example.net`

Specifies the root directory.
Corresponds to nginx [`root`][ngx_root] directive

#### tls
> Syntax: `tls: manual | letsencrypt | none`  
> Default: `tls: letsencrypt`

Specifies whether to enable SSL/TLS.

#### tls_params

Specifies path to needed files when `tls` is `manual`

See also nginx documentation for
[`ssl_certificate_key`][ngx_ssl_certificate_key],
[`ssl_certificate`][ngx_ssl_certificate],
[`ssl_trusted_certificate`][ngx_ssl_trusted_certificate]


#### php
> Syntax: `php: true | false`  
> Default: `php: false`

Enables PHP support through PHP-FPM


[ngx_server_name]: http://nginx.org/en/docs/http/ngx_http_core_module.html#server_name "Nginx: server_name"
[ngx_root]: http://nginx.org/en/docs/http/ngx_http_core_module.html#root "Nginx: root"
[ngx_ssl_certificate_key]: http://nginx.org/en/docs/http/ngx_http_ssl_module.html#ssl_certificate_key "Nginx: ssl_certificate_key"
[ngx_ssl_certificate]: http://nginx.org/en/docs/http/ngx_http_ssl_module.html#ssl_certificate "Nginx: ssl_certificate"
[ngx_ssl_trusted_certificate]: http://nginx.org/en/docs/http/ngx_http_ssl_module.html#ssl_trusted_certificate "Nginx: ssl_trusted_certificate"
[ngx_add_header]: http://nginx.org/en/docs/http/ngx_http_headers_module.html#add_header "Nginx: add_header"
[brutus_domain_id]: domain-module.md#id "Brutus: domain id"
