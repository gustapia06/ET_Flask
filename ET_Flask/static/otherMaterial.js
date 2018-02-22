function otherMaterial(val)
{
    var x1 = document.getElementsByClassName('new_material');
    var x2 = document.getElementsByClassName('new_i');
    var i;
    
    if (val==="other")
    {
        for (i=0; i<x1.length; i++)
        {
            x1[i].style.display = 'block';
        }
        for (i=0; i<x2.length; i++)
        {
            x2[i].required = true;
        }
    }
    else
    {
        for (i=0; i<x1.length; i++)
        {
            x1[i].style.display = 'none';
        }
        for (i=0; i<x2.length; i++)
        {
//            x2[i].pattern = ".+"
            x2[i].required = false;
        }
    }
}
