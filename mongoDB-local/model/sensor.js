const mongoose = require("mongoose")

const Sensor = new mongoose.Schema({
    plant_name: {type:String, required:true},
    plant_type: {type:String, required:true},
    soil_type: {type:String, default:""},
    moist_lvl: {type:Number, default:50},
    pot_size: {type:Number, required:true},
    last_care: {type:Date, default:0},
    care_lvl: {type:Number, required:true},
    position: {type:Number, default:0},
})

module.exports = mongoose.model("sensor_device",Sensor);
