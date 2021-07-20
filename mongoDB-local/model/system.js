const mongoose = require("mongoose")

const System = new mongoose.Schema({
    user_id: mongoose.Types.ObjectId,
    system_info:{
        x_size: {type:Number, default: 0},
        y_size: {type:Number, default: 0},
    },
    operation_box: {
        water_lvl: {type:Number, default: 0},
        position: Array,
        tank_size: Number,
    },
    sensor_device: Array,
})

module.exports = mongoose.model("System-Registry",System,"System-Registry");
