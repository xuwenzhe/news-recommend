const mongoose = require('mongoose');
const bcrypt = require('bcrypt');

const UserSchema = new mongoose.Schema({
  email: {
    type: String,
    index: {unique: true}
  },
  password: String  
});

// arrow function with 'this' is not safe here
UserSchema.methods.comparePassword = function comparePassword(password, callback) {
  bcrypt.compare(password, this.password, callback);
};
 
// necessary check before 'save' to the database
// arrow function with 'this' is not safe here
UserSchema.pre('save', function saveHook(next) { 
  const user = this;
  // proceed further only if the password is modified or the user is new
  if (!user.isModified('password')) return next();
  return bcrypt.genSalt((saltError, salt) => {
    if (saltError) {return next(saltError);}
    return bcrypt.hash(user.password, salt, (hashError, hash) => {
      if (hashError) {return next(hashError);}
      // replace a password string with hash value
      user.password = hash;
      return next();
    }); 
  });
});

module.exports = mongoose.model('User', UserSchema);