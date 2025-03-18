let mapOptions = {
    center:[ 13.93433842907902, 121.61332264989602 ],
    zoom:16
}
    
let map = new L.map('map' , mapOptions);
  
let layer = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
    map.addLayer(layer);

    // let marker = new L.Marker([13.93234887687673, 121.60557870426874]);
    // marker.addTo(map);