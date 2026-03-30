local str = require("Module:Strings")
local p = {}

--[[
------------
  Rarities
------------
Common = 1
Uncommon = 2
Rare = 3
Very Rare = 4
Ultra Rare = 5 (currently unused)
Teachable = 6 (currently unused)
Legendary = 7
Special Event = 8 (currently unused)
Artifact = 9 (currently unused)
Limited = 10 (currently unused)
Ascended = 12
Visceral = 13

-----------------
  All Cosmetics
-----------------
id = id of the cosmetic (MANDATORY)
name = name of the cosmetic
desc = description of the cosmetic
rarity = rarity of the cosmetic (MANDATORY)
filename = image file name
collectionId = id of the collection the cosmetic is in
default = true/false, whether the cosmetic is given to all players by default
purchasable = true/false, whether the cosmetic can be purchased
rDate = the date the cosmetic was released on, in the format "dd.mm.yyyy"
linked = true/false, whether the cosmetic is linked
ac = price in auric cells
is = price in iridescent shards
tome = id of the tome the cosmetic is from
riftPass = id of the rift pass the cosmetic is from
tier = which tier of the rift the cosmetic was rewarded at, if applicable
track = free/premium, which track of the rift the cosmetic was in, if applicable

-----------
  Outfits
-----------
fakeOutfit = true/false, set to true if the outfit is just one item like a shirt
pieces = {[category] = id of piece} (MANDATORY)
survivor/killer = id of the character linked to the outfit (MANDATORY)

---------------
  Collections
---------------
id = id of the collection
name = name of the collection

---------------------------------------------------
  The following data was automatically generated!
---------------------------------------------------
--]]