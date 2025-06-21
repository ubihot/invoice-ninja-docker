# Use a specific, stable version of PHP 8.2 for predictability
FROM php:8.2-fpm

WORKDIR /var/www/html

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    mariadb-client \
    nodejs \
    npm \
    git \
    unzip \
    zip\ 
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

# Install PHP extensions using the official installer for a cleaner setup
COPY --from=ghcr.io/mlocati/php-extension-installer /usr/bin/install-php-extensions /usr/local/bin/
RUN install-php-extensions pdo_mysql zip gd bcmath mbstring exif pcntl bcmath gd

# Configure PHP
# TODO understand this better
RUN ln -s "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"

# these will be beaten by the mounted volumes in the docker-compose
#COPY ./config/php/php.ini /usr/local/etc/php/conf.d/invoiceninja.ini
#COPY ./config/php/php-fpm.conf /usr/local/etc/php-fpm.d/invoiceninja.conf


# Copy Composer executable
# this copies the Composer executable from the official Composer image
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer


# --- This is where your custom code comes in ---
# Copy your local invoiceninja source code into the image
#


# the actual InvoiceNinja application source code is copied from your local machine into the container's working directory.
# TODO the question here is what do we copy?? eveything??
#COPY ./invoiceninja/ /var/www/html/

# two experiments
# - give it relative path
# - check what is in the original invoiceninja image that in the other project is pulled
#COPY ./invoiceninja/public /tmp/public  
#USER www-data

#COPY --exclude=./invoiceninja/node_modules --exclude=./invoiceninja/tests --exclude=./invoiceninja/.github ./invoiceninja .
COPY ./invoiceninja .

# Install application dependencies (these are now BAKED into the image)
# Executes Composer to install all the PHP dependencies defined in composer.json.
RUN composer install --no-interaction --no-scripts --prefer-dist




# PREPARE REACT FE
# https://github.com/invoiceninja/invoiceninja/blob/v5-stable/.github/workflows/react_release.yml#L42
COPY ./ui ./ui
#COPY ./ui/.env.example .ui.env 
# https://github.com/invoiceninja/invoiceninja/blob/0ea98ffe7dc29c6a3c42f7fa5b0474227858297c/.github/workflows/react_release.yml#L41C1-L41C31
WORKDIR /var/www/html/ui
RUN cp .env.example .env

COPY ../invoiceninja/vite.config.ts.react ./vite.config.js

# we are still in /var/www/html/ui
RUN npm install
RUN NODE_OPTIONS=--max-old-space-size=4096 npm run build
RUN cp -r ./dist/* ../public/

RUN mv ../public/index.html ../resources/views/react/index.blade.php

WORKDIR /var/www/html/

RUN npm install
RUN npm run production

# hmm I'm not sure about this but might be needed
# RUN ln -s ./resources/views/react/index.blade.php ./public/index.html


# Cleanup Builds
# https://github.com/invoiceninja/invoiceninja/blob/v5-stable/.github/workflows/react_release.yml#L54C15-L54C29
RUN rm -rf node_modules
RUN rm -rf .git
RUN rm -rf ./ui || true

# Set permissions: directories 755, files 644
RUN chmod -R a=r,u+w,a+X .

# Installs the JavaScript dependencies defined in package.json.

# Compiles the frontend assets (e.g., TypeScript/Sass into plain JavaScript/CSS) for production use.


# Every RUN command creates a new, permanent layer in the final image.


# creates a symbolic link at /var/www/html/public/storage that points to 
# the /var/www/html/storage/app/public directory
#RUN php artisan storage:link


#RUN mkdir -p /tmp/public 
RUN mv /var/www/html/public /tmp/public




## Copy supervisor and php configurations
# Copies the Supervisor configuration file into the image. This file defines what processes Supervisor should start and monitor (e.g., php-fpm).
#COPY config/supervisor/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# critical for Laravel. It changes the ownership of the storage and bootstrap/cache directories to the www-data user, allowing the web server to write logs, cache files, and file uploads. 
#RUN chown -R www-data:www-data /var/www/html/storage /var/www/html/bootstrap/cache \
#    && chmod -R 777 /var/www/html/storage /var/www/html/bootstrap/cache

# Add initialization script
# Copies an initialization script (init.sh) into the image and makes it executable. 
COPY --chmod=0755 scripts/init.sh /usr/local/bin/init.sh

# Configures Docker to periodically check if the container is healthy by running the specified command. Here, it checks if the php-fpm master process is running.
#HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
#    CMD pgrep -f "php-fpm: master process"

# Sets the main command to be executed when the container starts. The init.sh script will run.
#ENTRYPOINT ["/usr/local/bin/init.sh"]
# Provides the default command to the entrypoint.
# A common pattern for an init.sh script is to perform its setup tasks and then execute the command passed as an argument.
# In this case, after init.sh finishes, it will start supervisord, which in turn starts and manages the php-fpm service, keeping the container running.
#CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
#

# as configuring a container to run as a specific executable.
# The command and parameters you provide when you run the container are appended as arguments to the ENTRYPOINT.
# ENTRYPOINT ["ls"]
# CMD ["-a"]
# CMD is short for command. TODO verify
#CMD ["google.com"] # this becomes an arg to `ping` in ENTRYPOINT





ENTRYPOINT ["/usr/local/bin/init.sh"]
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]


# a default, easily overridable command for a container. 
# - If you run docker run my-node-app, the container will execute node server.js.
# - However, if you run docker run my-node-app ls -l, you completely replace the default CMD. The container will execute ls -l instead of starting the server.
#CMD ["node", "server.js"]







