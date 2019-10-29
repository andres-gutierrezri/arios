function checkLength(long,ele){
  let fieldLength = ele.value.length;
  if(fieldLength <= long){
    return true;
  }
  else
  {
    let str = ele.value;
    str = str.substring(0, str.length - 1);
    ele.value = str;
  }
}