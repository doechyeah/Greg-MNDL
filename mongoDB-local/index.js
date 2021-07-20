const express = require("express");
const mongoose = require("mongoose");
const System = require("./model/system");
const Sensor = require("./model/sensor");
const app = express();
const User = require("./model/user");
const Plant = require("./model/plant");

require("dotenv/config");
app.use(express.json());

mongoose.connect(
    process.env.DB_CONNECTION_STRING_TEST,
    {useNewUrlParser: true,  useUnifiedTopology: true},
    (req, res) =>{
    console.log("connect to the mongodb");
});// connect to the mongodb altas


app.post("/create-user", async (req, res)=>{
    try{
        const myuser = new User({
            username: req.body.username,
            password: req.body.password,
        });
        await myuser.save();
        res.send(myuser);
    }catch(err){
        res.send({message: err});
    }
});// create a new user

app.post("/user-login", async (req,res)=>{
   try{
       User.findOne({ username: req.body.username }, function (err, result) {
            if(result){
                if(result.username == req.body.username && result.password == req.body.password){
                    console.log(result);
                   res.status(200).json(result)
                    // res.send(result._id)
                }
            }else {
                res.send({})
            }
       });
   }catch (err) {
       res.send({message: err});
   }
});

app.put("/operationBox-setup", async(req, res)=>{
    try{
        let sysIDreq = mongoose.Types.ObjectId(req.body.system_id);
        let update = {
            "operation_box.water_lvl": req.body.water_lvl,
            "operation_box.position": req.body.position,
            "operation_box.tank_size": req.body.tank_size,
        }
        System.findByIdAndUpdate(sysIDreq, update, function (err, result) {
            if(!err){
                res.json(result)
            }
        })
    }catch (err) {
        res.send(err);
    }
});

app.post("/register-system", async(req,res)=> {
    try {
        let session = await System.startSession()
        session.startTransaction()
        var usrIDreq = mongoose.Types.ObjectId(req.body.user_id);
        const mysys = new System({
            user_id: usrIDreq,
            system_info:{
                x_size: req.body.x_size,
                y_size: req.body.y_size,
            },
            operation_box:{
                water_lvl: req.body.water_lvl,
                position: req.body.position,
                tank_size: req.body.tank_size,
            },
            sensor_device: req.body.sensors,
        });
        let a = await mysys.save();
        let b = await User.findByIdAndUpdate(mysys.user_id, {$addToSet: {user_sys: [mysys._id]} });
        await session.commitTransaction();
        session.endSession();
        res.json(mysys);
    } catch(err) {
        res.send({message: err});
    }
});// Register a new system to a user

app.post("/register-sensor", async (req,res)=>{
    try {
        let session = await System.startSession()
        session.startTransaction()
        const mysens = new Sensor({
            plant_name: req.body.plant_name,
            plant_type: req.body.plant_type,
            pot_size: req.body.pot_size,
            care_lvl: req.body.care_lvl,
        });
        let status = await System.findByIdAndUpdate(req.body.sys_id, {$addToSet: {sensor_device: mysens} });
        await session.commitTransaction();
        session.endSession();
        res.send(mysens._id);
    } catch (err) {
        res.send({message: err});
    }
})

app.get("/system_plants", async (req,res)=>{
    try {
        let sensor_list = await System.findById(req.body.sys_id, "sensor_device").exec();
        res.json(sensor_list.sensor_device);
    } catch(err) {
        res.send({message: err});
    }
})

app.get("/plant_info", async (req,res)=>{
    try {
        let sensor_list = await System.findById(req.body.sys_id, "sensor_device").exec();
        let plant_info = sensor_list.sensor_device.find(x => x._id ==req.body.plant_id);
        res.json(plant_info);
    } catch(err) {
        res.send({message: err});
    }
})

app.get("/user_systems", async (req,res)=>{
    try {
        let system_list = await User.findById(req.body.user_id, "user_sys").exec();
        res.json(system_list);
    } catch(err) {
        res.send({message: err});
    }
})

app.delete("/delete_system", async (req, res) => {
    try{
        let session = await System.startSession()
        session.startTransaction()
        let sysIDreq = mongoose.Types.ObjectId(req.body.system_id);
        let userIDreq = mongoose.Types.ObjectId(req.body.user_id);
        let a = await System.findByIdAndDelete(sysIDreq);
        let b = await User.findByIdAndUpdate(userIDreq,{ $pullAll: {user_sys: [sysIDreq] } });
        await session.commitTransaction();
        session.endSession();
        res.send({message: "Successfully Deleted"});
    } catch (err) {
        res.send({message: err})
    }
})

app.delete("/delete_sensor", async (req, res) => {
    try{
        let sysIDreq = mongoose.Types.ObjectId(req.body.system_id);
        let sensorIDreq = mongoose.Types.ObjectId(req.body.sensor_id);
        console.log(sysIDreq);
        console.log(sensorIDreq);
        await System.findByIdAndUpdate(sysIDreq,{$pull: {"sensor_device": { "_id": sensorIDreq}}});
        res.send({message: "Successfully Deleted"});
    } catch (err) {
        res.send({message: err})
    }
})

app.listen(3000, () =>{
    console.log("Listen to 3000")
})// suggest to use postman to make a api call
