1. `sudo apt install geoipupdate`
2. `nano /etc/GeoIP.conf`
   ```
   AccountID xxx
   LicenseKey xxx
   EditionIDs GeoLite2-Country
   ```
3. `systemctl enable --now geoipupdate.timer`
4. `systemctl start geoipupdate`
5. `file /var/lib/GeoIP/GeoLite2-Country.mmdb`