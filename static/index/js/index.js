$(function(){
    switchmain("推荐");
    $("#xiala").click(function(){
        $(".min").css("display","none");
        $(".max").css("display","block");
    })
    $("#xiala1").click(function(){
        $(".min").css("display","block");
        $(".max").css("display","none");
    })

    $(".min").click(function(e){
        if(e.target.nodeName=="LI"){
            let index=$(".min ul li").index(e.target)
            $(".min ul li").removeClass("hot").eq(index).addClass("hot");
            $(".max ul li").removeClass("hot").eq(index).addClass("hot");
            switchmain($(e.target).html())
        }
    })
    $(".max").click(function(e){
        if(e.target.nodeName=="LI"){
            let index=$(".max ul li").index(e.target)
            $(".max ul li").removeClass("hot").eq(index).addClass("hot");
            $(".min ul li").removeClass("hot").eq(index).addClass("hot");
            switchmain($(e.target).html())
        }
    })


    $("#man").click(function(){
        $(".login").animate({
            width:"100%"
        },1000)
    })
    $(".headers i").click(function(){
        $(".login").css("width","0")
    })


    function switchmain(str){
        $.ajax({
            url:'/index/switchindex'+str,
            success:function(e){
            $(".mainbox").children().remove()
            for(let i=0;i<e.length;i++){
                if(e[i][9]==0){
                    $(".mainbox").append($(`
                        <li><a href="/index/opendetails${e[i][0]}">
                            <h3>${e[i][1]}</h3>
                            <div class="bottom">
                                <h5>${e[i][2]}</h5>
                            </div>
                        </a></li>
                    `))
                }else if(e[i][9]>0&&e[i][9]<3){
                    $(".mainbox").append($(`
                        <li><a href="/index/opendetails${e[i][0]}">
                            <div class="left">
                                <img src="${e[i][3][0]}" alt="">
                            </div>
                            <div class="right">
                                <h3>${e[i][1]}</h3>
                                <div class="bottom">
                                    <h5>${e[i][2]}</h5>
                                    <h6>热点</h6>
                                </div>
                            </div>
                        </a></li>`))
                }else{
                    $(".mainbox").append($(`
                        <li><a href="/index/opendetails${e[i][0]}">
                            <h3>${e[i][1]}</h3>
                            <div class="imgbottom">
                                <img src="${e[i][3][0]}" alt="">
                                <img src="${e[i][3][1]}" alt="">
                                <img src="${e[i][3][2]}" alt="">
                            </div>
                            <div class="bottom">
                                <h5>${e[i][2]}</h5>
                                <h6>热点</h6>
                            </div>
                        </a></li>
                    `))
                    }
            }
            }
            })
    }

    $("#sousuo").click(function(){
        if($("#sousuo_input").css("display")=="none"){
            $("#sousuo_input").show("slow").focus()
            $("#sousuo_input").val("")
        }else if($("#sousuo_input").css("display")=="block"){
            let con=$("#sousuo_input").val()
            $.ajax({
                url:'/index/ss_keyword',
                type:'post',
                data:{'con':con},
                success:function(e){
                    $(".mainbox").children().remove()
                    if(e['flag']==1){
                        for(let i=0;i<e['tuijian'].length;i++){
                            if(e['tuijian'][i][4]==0){
                                $(".mainbox").append($(`
                                    <li><a href="/index/opendetails${e['tuijian'][i][0]}">
                                        <h3>${e['tuijian'][i][1]}</h3>
                                        <div class="bottom">
                                            <h5>${e['tuijian'][i][2]}</h5>
                                        </div>
                                    </a></li>
                                `))
                            }else if(e['tuijian'][i][4]>0&&e['tuijian'][i][4]<3){
                                $(".mainbox").append($(`
                                    <li><a href="/index/opendetails${e['tuijian'][i][0]}">
                                        <div class="left">
                                            <img src="${e['tuijian'][i][3][0]}" alt="">
                                        </div>
                                        <div class="right">
                                            <h3>${e['tuijian'][i][1]}</h3>
                                            <div class="bottom">
                                                <h5>${e['tuijian'][i][2]}</h5>
                                                <h6>热点</h6>
                                            </div>
                                        </div>
                                    </a></li>`))
                            }else{
                                $(".mainbox").append($(`
                                    <li><a href="/index/opendetails${e['tuijian'][i][0]}">
                                        <h3>${e['tuijian'][i][1]}</h3>
                                        <div class="imgbottom">
                                            <img src="${e['tuijian'][i][3][0]}" alt="">
                                            <img src="${e['tuijian'][i][3][1]}" alt="">
                                            <img src="${e['tuijian'][i][3][2]}" alt="">
                                        </div>
                                        <div class="bottom">
                                            <h5>${e['tuijian'][i][2]}</h5>
                                            <h6>热点</h6>
                                        </div>
                                    </a></li>
                                `))
                            }
                        }
                    }else{
                        $(".mainbox").append($(`<li><h3>无相关内容推荐</h3></li>`))
                    }
                    $("#sousuo_input").hide("slow")

                }
                })
            }
        })
})

