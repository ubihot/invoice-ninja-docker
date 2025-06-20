## Use a specific, stable version of PHP 8.2 for predictability
#FROM php:8.2-fpm

#WORKDIR /var/www/html

## Install system dependencies, including supervisor, mysql client, and PDF tools
## This is adapted from the official InvoiceNinja Dockerfile for robustness
## RUN apt-get update && apt-get install -y --no-install-recommends \
##     git \
##     unzip \
##     zip \
##     mariadb-client \
##     gpg \
##     supervisor \
##     nodejs \
##     npm \
##     # PDF & Font Support
##     fonts-noto-cjk-extra fonts-wqy-microhei fonts-wqy-zenhei xfonts-wqy \
##     && apt-get clean && rm -rf /var/lib/apt/lists/*

## # Install Google Chrome for PDF generation (crucial for production)
## RUN apt-get update && apt-get install -y --no-install-recommends \
##     && if [ "$(dpkg --print-architecture)" = "amd64" ]; then \
##     mkdir -p /etc/apt/keyrings \
##     && curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google.gpg \
##     && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google.gpg] https://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
##     && apt-get update && apt-get install -y --no-install-recommends google-chrome-stable; \
##     elif [ "$(dpkg --print-architecture)" = "arm64" ]; then \
##     apt-get install -y --no-install-recommends chromium; \
##     fi \
##     && apt-get purge -y gpg \
##     && apt-get autoremove -y \
##     && apt-get clean && rm -rf /var/lib/apt/lists/*

## Install system dependencies
#RUN apt-get update && apt-get install -y --no-install-recommends \
    #mariadb-client \
    #nodejs \
    #npm \
    #git \
    #unzip \
    #zip\ 
    #gpg \
    #supervisor \
    ## Unicode support for PDF
    #fonts-noto-cjk-extra \
    #fonts-wqy-microhei \
    #fonts-wqy-zenhei \
    #xfonts-wqy \
    ## Install google-chrome-stable(amd64)/chromium(arm64)
    #&& if [ "$(dpkg --print-architecture)" = "amd64" ]; then \
    #mkdir -p /etc/apt/keyrings \
    #&& curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | \
    #gpg --dearmor -o /etc/apt/keyrings/google.gpg \
    #&& echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google.gpg] https://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    #&& apt-get update \
    #&& apt-get install -y --no-install-recommends google-chrome-stable; \
    #elif [ "$(dpkg --print-architecture)" = "arm64" ]; then \
    #apt-get install -y --no-install-recommends \
    #chromium; \        
    #fi \
    ## Create config directory for chromium/google-chrome-stable
    #&& mkdir /var/www/.config \
    #&& chown www-data:www-data /var/www/.config \
    ## Cleanup
    #&& apt-get purge -y gpg \
    #&& apt-get autoremove -y \
    #&& apt-get clean \
    #&& rm -rf /var/lib/apt/lists/*

## Install PHP extensions using the official installer for a cleaner setup
#COPY --from=ghcr.io/mlocati/php-extension-installer /usr/bin/install-php-extensions /usr/local/bin/
#RUN install-php-extensions pdo_mysql zip gd bcmath mbstring exif pcntl bcmath gd

## Configure PHP
#RUN ln -s "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"

#COPY ./config/php/php.ini /usr/local/etc/php/conf.d/invoiceninja.ini

#COPY ./config/php/php-fpm.conf /usr/local/etc/php-fpm.d/invoiceninja.conf


## Copy Composer executable
#COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

## --- This is where your custom code comes in ---
## Copy your local invoiceninja source code into the image
#RUN mkdir -p /tmp/public 

#COPY ./invoiceninja/ /var/www/html/


## Install application dependencies (these are now BAKED into the image)
#RUN composer install --no-interaction --no-scripts --prefer-dist

#RUN npm install

#RUN npm run build

## Create tmp/public and copy build output

## --- End of custom code section ---

## Copy supervisor and php configurations
#COPY config/supervisor/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

## Set correct permissions for storage and cache
#RUN chown -R www-data:www-data /var/www/html/storage /var/www/html/bootstrap/cache \
    #&& chmod -R 777 /var/www/html/storage /var/www/html/bootstrap/cache

## Add initialization script
#COPY --chmod=0755 scripts/init.sh /usr/local/bin/init.sh

## Health check
#HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    #CMD pgrep -f "php-fpm: master process"

#ENTRYPOINT ["/usr/local/bin/init.sh"]
#CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

ARG PHP=8.3

FROM php:${PHP}-fpm AS prepare-app

USER www-data

RUN curl -sL "https://github.com/invoiceninja/invoiceninja/releases/latest/download/invoiceninja.tar.gz" | \
    tar -xz -C /var/www/html \
    && ln -s /var/www/html/resources/views/react/index.blade.php /var/www/html/public/index.html \
    && php artisan storage:link \
    # Workaround for application updates
    && mv /var/www/html/public /tmp/public

# ==================
# InvoiceNinja image
# ==================
FROM php:${PHP}-fpm

# PHP modules
ARG php_require="bcmath gd mbstring pdo_mysql zip"
ARG php_suggest="exif imagick intl pcntl saxon soap"
ARG php_extra="opcache"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    mariadb-client \
    gpg \
    supervisor \
    # Unicode support for PDF
    fonts-noto-cjk-extra \
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    xfonts-wqy \
    # Install google-chrome-stable(amd64)/chromium(arm64)
    && if [ "$(dpkg --print-architecture)" = "amd64" ]; then \
    mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | \
    gpg --dearmor -o /etc/apt/keyrings/google.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google.gpg] https://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable; \
    elif [ "$(dpkg --print-architecture)" = "arm64" ]; then \
    apt-get install -y --no-install-recommends \
    chromium; \        
    fi \
    # Create config directory for chromium/google-chrome-stable
    && mkdir /var/www/.config \
    && chown www-data:www-data /var/www/.config \
    # Cleanup
    && apt-get purge -y gpg \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
COPY --from=ghcr.io/mlocati/php-extension-installer /usr/bin/install-php-extensions /usr/local/bin/

RUN install-php-extensions \
    ${php_require} \
    ${php_suggest} \
    ${php_extra}

# Configure PHP
RUN ln -s "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"

COPY php/php.ini /usr/local/etc/php/conf.d/invoiceninja.ini

COPY php/php-fpm.conf /usr/local/etc/php-fpm.d/invoiceninja.conf

# Setup supervisor
COPY supervisor/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Setup InvoiceNinja
COPY --from=prepare-app /var/www/html /var/www/html
COPY --from=prepare-app /tmp/public /tmp/public

# Add initialization script
COPY --chmod=0755 scripts/init.sh /usr/local/bin/init.sh

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD pgrep -f "php-fpm: master process"

ENTRYPOINT ["/usr/local/bin/init.sh"]
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
