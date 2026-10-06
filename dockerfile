FROM php:8.2-apache

RUN a2enmod rewrite

COPY php.ini /usr/local/etc/php/conf.d/uploads.ini

WORKDIR /var/www/html

EXPOSE 80