<?xml version="1.0" encoding="UTF-8"?>
<tileset version="1.2" tiledversion="1.3.3" name="big_entities.tsk" tilewidth="48" tileheight="48" tilecount="4" columns="2">
 <tileoffset x="6" y="53"/>
 <properties>
  <property name="tileset_property" type="bool" value="false"/>
 </properties>
 <image source="entities.png" width="128" height="128"/>
 <terraintypes>
  <terrain name="New Terrain" tile="0">
   <properties>
    <property name="asdf" value="terrainprop"/>
   </properties>
  </terrain>
 </terraintypes>
 <tile id="0">
  <properties>
   <property name="function" value="goomba"/>
  </properties>
  <objectgroup draworder="index" id="2">
   <object id="1" x="0.130435" y="47.8696">
    <polygon points="0,0 16.2174,-0.173913 15.1304,-11.6522 9.86957,-15.6957 5.47826,-15.6522 0.304348,-10.913"/>
   </object>
   <object id="2" x="0.205002" y="0.192704" width="19.2727" height="8.90909" rotation="24.7525">
    <ellipse/>
   </object>
  </objectgroup>
  <animation>
   <frame tileid="0" duration="300"/>
   <frame tileid="3" duration="300"/>
  </animation>
 </tile>
 <tile id="1" type="MyType" terrain=",0,0,0" probability="2">
  <properties>
   <property name="function" value="mario"/>
   <property name="type" value="asdf"/>
  </properties>
  <objectgroup draworder="index" id="2">
   <object id="1" x="-0.877051" y="46.4904" rotation="10.5739">
    <polygon points="0,0 5,-2.17391 10.2174,-0.26087 12.6087,-4.86957 10.5217,-7.69565 9.17391,-17.3478 2.65217,-15.7826 -0.130435,-5.13043"/>
   </object>
  </objectgroup>
 </tile>
 <tile id="3" terrain=",0,,0">
  <objectgroup draworder="index" id="2">
   <object id="1" x="22.2195" y="7.3012" rotation="74.2579">
    <polyline points="-1.09091,4.94719 21.8182,-1.97888 27.4545,12.2973 10.9091,19.6474"/>
   </object>
  </objectgroup>
 </tile>
 <wangsets>
  <wangset name="New Wang Set" tile="-1">
   <wangedgecolor name="" color="#ff0000" tile="-1" probability="1"/>
   <wangedgecolor name="" color="#00ff00" tile="-1" probability="1"/>
   <wangtile tileid="1" wangid="0x2010100"/>
   <wangtile tileid="3" wangid="0x202"/>
   <properties>
    <property name="afasdf" value="wangprop"/>
   </properties>
  </wangset>
 </wangsets>
</tileset>
