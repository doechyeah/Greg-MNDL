const mongoose = require("mongoose")

const User = new mongoose.Schema({
    username: {type: String, unique: true},
    password: String,
    user_sys: Array,
})

module.exports = mongoose.model("User-Registry",User,"User-Registry");
