<template>
    <div>
        <v-dialog
        v-model="dialog"
        max-width="350"
    >
        <v-card>
            <v-container>
                <v-row
                    align-content="center"
                    align="center"
                >
                    <v-col cols=3 class="mt-6">
                        <v-icon
                            large
                            right
                            color="red"
                        >mdi-alert-circle</v-icon>
                    </v-col>
                    <v-col cols=9 class="mt-6">
                        <v-card-text class="text-subtitle-1">This file format is not supported</v-card-text>
                        <v-card-text class="text-subtitle-2">Supported format: GeoTIFF</v-card-text>
                    </v-col>
                </v-row>
            </v-container>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                    text
                    color="primary"
                    @click="dialog=false"
                >Close</v-btn>
            </v-card-actions>

        </v-card>
    </v-dialog>
        <Loading :loaded="loaded"/>
        <v-container v-if="loaded">
            <!--add the widget content here -->
            <v-stepper
                v-model="stepper"
                vertical
            >
                <v-stepper-step
                    :complete="stepper > 1"
                    :editable="editable.step1"
                    step="1"                
                >
                    Choose local file(s)
                </v-stepper-step>
                <v-stepper-content step="1">
                    <v-list dense>
                    <v-subheader v-text="items[0].value.length == 2 ? 'All drives': items[0].value.slice(0,items[0].value.length-3)"></v-subheader>
                    <v-list-item-group
                        v-model="selectedItem"
                        color="primary"
                    >
                        <v-list-item
                        v-for="(item, i) in items"
                        :key="i"
                        @click="entityClicked(item.value)"
                        >
                        <v-list-item-icon>
                            <v-icon v-text="item.icon"></v-icon>
                        </v-list-item-icon>
                        <v-list-item-content>
                            <v-list-item-title v-text="item.text"></v-list-item-title>
                        </v-list-item-content>
                        </v-list-item>
                    </v-list-item-group>
                    </v-list>
                </v-stepper-content>
                <v-stepper-step step="2">
                    Done!
                </v-stepper-step>
                <v-stepper-content step="2">
                    <v-card elevation="3" outlined class="mb-3">
                        <v-card-text class="text-body-2">
                            You may now move the scene around.
                        </v-card-text>
                    </v-card>
                </v-stepper-content>
            </v-stepper>
            <!-- <v-btn
                class="my-6"
                block
                color="primary"
                @click="startover"
            >
                Clear
            </v-btn> -->
        </v-container>
    </div>
</template>
<script>
import getConfig from "@/mixins/getConfig.js"
import loadModules from "@/mixins/loadModules.js"
import Loading from "@/components/Loading"

export default {
    name: "ReadTiff",

    props: {

    },

    data(){
        return{
            view: this.$view,
            config: null,
            loaded: false,
            dialog: false,
            
            items: [
                { text: 'Parent directory', icon: 'mdi-keyboard-backspace'},
                { text: 'LoremIpsum', icon: 'mdi-folder' },
                { text: 'DolorSitAmet', icon: 'mdi-folder' },
                { text: 'StarVision.tif', icon: 'mdi-file-image' },
            ],
            stepper: 1,
            editable: {
                step1: true,
                step2: false,
                step3: false
            },
            selectedItem: null,
            files: [],
            submitDisabled: true,
            models: [],
            model: null,
            addBtnDisabled: true,
            cancelBtnDisabled: true,
            createEventListener: null,
            selectModelEventListener: null,
            glLength: 0,
            selectedModel: [],
            deleteBtnDisabled: true,
            displayModels: true
        };
    },

    mixins: [
        getConfig("configs/widgets/Import3DModels/config.json"),
        loadModules(["esri/layers/BaseTileLayer","esri/geometry/projection"]),
    ],
    
    components: {
        Loading
    },    

    computed: {
        selectedModelLength: function(){
            return this.selectedModel.length;
        }
    },

    methods:{
        init: function([BaseTileLayer, projection]){
            this.getConfig().then(config => {
                this.view.when(() => {
                    this.config = config;

                    this.loaded = true;

                    this.BaseTileLayer = BaseTileLayer;
                    this.projection = projection;
                    this.projection.load();
                    this.changeDirectory('C:');
                });
            });

        },

        entityClicked: function(e) {
            console.log(e);
            if(e.endsWith('.tif')){
                this.readFile(e);
            } else {
                this.changeDirectory(e);
            }
        },

        changeDirectory: function(pwd) {
            fetch(`http://localhost:18080/cd?pwd=${pwd}`).then(x=>x.json().then((json)=> {
                this.items = json;
                this.selectedItem = null;
            }));
        },

        readFile: function(filename) {
            this.stepper = 2;
                console.log(filename);

                // Use the file name only
                fetch(`http://localhost:18080/warpextent?filename=${filename}`).then(x=>x.json().then(response=>{
                    console.log(response);
                    //Project extent to WebMercator
                    let minExtent = this.projection.project({
                        type: "point",
                        x: response[0],
                        y: response[1],
                        spatialReference:{wkid:2326}
                    }, {
                        wkid: 102100
                    });

                    let maxExtent = this.projection.project({
                        type: "point",
                        x: response[2],
                        y: response[3],
                        spatialReference: { wkid:2326 }
                    }, {
                        wkid: 102100
                    });

                    //Create the layer here
                    this.BaseTileLayer.createSubclass








                    let bdl = this.BaseTileLayer.createSubclass({
                        getTileUrl: function (level, row, col) {
                            if (level < 15 || level > 22) {
                                return false;
                            }

                            let extent = this.getTileBounds(level, row, col);

                            let side = 256;

                            //localhost
                            return `http://localhost:18080/warp?filename=${filename}&level=${level}&row=${row}&col=${col}&xmin=${extent[0]}&ymin=${extent[1]}&xmax=${extent[2]}&ymax=${extent[3]}&side=${side}&bands=${response[4]}`
                            //return `http://demo2.hkgisportal.com/warp?level=${level}&row=${row}&col=${col}&xmin=${extent[0]}&ymin=${extent[1]}&xmax=${extent[2]}&ymax=${extent[3]}&width=${width}&height=${height}`
                        //return this.urlTemplate.replace("{z}", level).replace("{x}", col).replace("{y}", row);
                        }
                    });

                    let splitFilename=filename.split('/');

                    let bdl_ = new bdl({
                        fullExtent: {
                                xmin: minExtent.x,
                                ymin: minExtent.y,
                                xmax: maxExtent.x,
                                ymax: maxExtent.y,
                                spatialReference: { wkid: 102100 }
                            },
                        title: splitFilename.slice(splitFilename.length-1)
                    });

                    this.view.map.add(bdl_);
                    window._sceneView= this.view;
                    this.view.goTo(bdl_.fullExtent);
                }))
        },

        startover: function(){
            this.graphicsLayer.removeAll();
            this.files = [];
            this.models = [];
            this.model = null;
        }
    },

    created: function(){
        this.getModules().then(this.init);
    }


}
</script>
<style lang="scss">
@import '@/styles/variables.scss';
</style>