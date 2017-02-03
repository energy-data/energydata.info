mapboxgl.accessToken = 'pk.eyJ1IjoiZG1vcmlhcnR5IiwiYSI6Ikd3T29EOWMifQ.-DKJ4ernht84AZmc6Bk51Q';
var map_1 = new mapboxgl.Map({
    container: 'ssa-aicd-electricity-map',
    style: '/data/map-style.json',
    center: [60, 2.867],
    zoom: 1.5
});

map_1.on('load', function () {
  map_1.addLayer({
    "id": 'data-layer-kano',
    "type": 'line',
    "source": {
      "type": "geojson",
      "data": "/data/aicd-eletricity-clean.geojson"
    },
    'layout': {
      'line-join': 'round',
      'line-cap': 'round'
    },
    "paint":{
      "line-color": 'rgb(34, 166, 245)',
      "line-width": 1
    }
  })
})

var map_2 = new mapboxgl.Map({
    container: 'kano-electricity-distribution-map',
    style: '/data/map-style.json',
    center: [9.5, 11.999],
    zoom: 7.2
});

map_2.on('load', function () {
  map_2.addLayer({
    "id": 'data-layer',
    "type": 'line',
    "source": {
      "type": "geojson",
      "data": "/data/aicd-eletricity-clean.geojson"
    },
    'layout': {
      'line-join': 'round',
      'line-cap': 'round'
    },
    "paint":{
      "line-color": 'rgb(34, 166, 245)',
      "line-width": 1
    }
  })
})
