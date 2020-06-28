<?xml version="1.0" encoding="UTF-8"?>
<tileset version="1.2" tiledversion="1.3.3" name="terrain.tsk" tilewidth="16" tileheight="16" tilecount="64" columns="8">
 <tileoffset x="8" y="8"/>
 <image source="terrain.png" width="128" height="128"/>
 <terraintypes>
  <terrain name="platforms" tile="25"/>
 </terraintypes>
 <tile id="0" terrain=",,,0"/>
 <tile id="1" terrain=",,0,0"/>
 <tile id="2" terrain=",,0,"/>
 <tile id="3" terrain=",0,0,"/>
 <tile id="8" terrain=",0,,0"/>
 <tile id="9" terrain="0,0,0,0"/>
 <tile id="10" terrain="0,,0,"/>
 <tile id="11" terrain="0,,0,0"/>
 <tile id="16" terrain=",0,,"/>
 <tile id="17" terrain="0,0,,"/>
 <tile id="18" terrain="0,,,"/>
 <tile id="19" terrain="0,0,,0"/>
 <tile id="24" terrain="0,,,0"/>
 <tile id="25" terrain=",0,0,0">
  <animation>
   <frame tileid="25" duration="100"/>
   <frame tileid="57" duration="100"/>
  </animation>
 </tile>
 <tile id="26" terrain="0,0,0,"/>
</tileset>
