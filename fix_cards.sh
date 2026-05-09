#!/bin/bash
F=/app/.next/server/app/index.html

# Backup
docker exec kloud-web cp $F ${F}.bak

# Smart Analysis -> /modules/eeg-analysis
docker exec kloud-web sed -i 's/text-center"><div class="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-500/text-center cursor-pointer" onclick="location.href='"'"'\/modules\/eeg-analysis'"'"'"><div class="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-500/g' $F

# Creative Tools -> /modules/curiosity-ocean
docker exec kloud-web sed -i 's/text-center"><div class="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-teal-400 to-emerald-500/text-center cursor-pointer" onclick="location.href='"'"'\/modules\/curiosity-ocean'"'"'"><div class="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-teal-400 to-emerald-500/g' $F

# Seamless Experience -> /modules
docker exec kloud-web sed -i 's/text-center"><div class="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-amber-400 to-orange-500/text-center cursor-pointer" onclick="location.href='"'"'\/modules'"'"'"><div class="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-amber-400 to-orange-500/g' $F

echo "Done! 3 cards are now clickable"

