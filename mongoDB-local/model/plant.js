const mongoose = require("mongoose");

const Plant = new mongoose.Schema({
    species: String,
    moisture: String,
    ideal_soil: String,
    scale_factor:{type:Number, default: 1}
});

module.exports = mongoose.model("Plant-Registry",Plant,"Plant-Registry");
