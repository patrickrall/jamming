<?xml version="1.0" encoding="UTF-8"?>
<tileset version="1.4" tiledversion="1.4.1" name="terrain.tsk" tilewidth="16" tileheight="16" tilecount="64" columns="8">
 <tileoffset x="8" y="8"/>
 <image source="terrain.png" width="128" height="128"/>
 <terraintypes>
  <terrain name="platforms" tile="25"/>
 </terraintypes>
 <tile id="0" terrain=",,,0">
  <objectgroup draworder="index" id="2">
   <object id="2" x="8.0625" y="8.0625" width="7.875" height="7.875"/>
  </objectgroup>
 </tile>
 <tile id="1" terrain=",,0,0">
  <objectgroup draworder="index" id="2">
   <object id="1" x="-0.0625" y="8" width="16" height="8"/>
  </objectgroup>
 </tile>
 <tile id="2" terrain=",,0,">
  <objectgroup draworder="index" id="2">
   <object id="1" x="0.0625" y="7.9375" width="7.875" height="8"/>
  </objectgroup>
 </tile>
 <tile id="3" terrain=",0,0,"/>
 <tile id="8" terrain=",0,,0">
  <objectgroup draworder="index" id="2">
   <object id="1" x="9.0625" y="0" width="6.8125" height="15.875"/>
  </objectgroup>
 </tile>
 <tile id="9" terrain="0,0,0,0"/>
 <tile id="10" terrain="0,,0,">
  <objectgroup draworder="index" id="2">
   <object id="1" x="0.0625" y="-0.0625" width="6.9375" height="16.125"/>
  </objectgroup>
 </tile>
 <tile id="11" terrain="0,,0,0"/>
 <tile id="16" terrain=",0,,">
  <objectgroup draworder="index" id="2">
   <object id="1" x="9" y="0.0625" width="7" height="7.8125"/>
   <object id="2" x="9" y="7.875">
    <polygon points="0,0 -1.9375,6.4375 5.375,5.5625"/>
   </object>
  </objectgroup>
 </tile>
 <tile id="17" terrain="0,0,,">
  <objectgroup draworder="index" id="2">
   <object id="1" x="0" y="0" width="15.9375" height="7.9375"/>
  </objectgroup>
 </tile>
 <tile id="18" terrain="0,,,">
  <objectgroup draworder="index" id="2">
   <object id="1" x="-0.0625" y="0.0625" width="7" height="7.8125"/>
  </objectgroup>
 </tile>
 <tile id="19" terrain="0,0,,0"/>
 <tile id="24" terrain="0,,,0"/>
 <tile id="25" terrain=",0,0,0"/>
 <tile id="26" terrain="0,0,0,"/>
</tileset>
