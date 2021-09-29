#------------------------------------------------------------------------------
# Copyright 2018 Esri
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------
# Name: Feature_service.py
# Description: This is a utility program which is used to upload feature services to portal.
# Version: 2.3
# Date Created : 20181009
# Date updated : 20191126
# Requirements: ArcGIS Pro 2.2
# Author: Esri Imagery Workflows team
#------------------------------------------------------------------------------

import os
import json
import requests
import tempfile
import arcpy

dir_path = os.path.dirname(__file__)

class FeatureServiceUtil(object):

    def __init__(self, portal_username, portalurl):
        self._portalurl = portalurl
        self._portal_username = portal_username

    def _get_result_status(self, success, message, **kwargs):
        result_status = {"success": success, "message": message}
        result_status.update(kwargs)
        return result_status

    def _get_portal_token(self):
        return arcpy.GetSigninToken()['token']

    def _get_features(self, feature_class_path):
        try:
            features = []
            with (arcpy.da.SearchCursor(feature_class_path,["SHAPE@JSON","*"])) as cursor:
                for row in cursor:
                    fields = cursor.fields
                    fields = fields[1:] #skip geometry
                    geometry = json.loads(row[0])
                    row = row[1:]
                    attributes = dict(zip(fields, row))
                    attributes.pop('AcquisitionDate')
                    feature = {'geometry': geometry,
                               'attributes': attributes}
                    features.append(feature)
            return self._get_result_status(success=True, message='',
                                           features=features)
        except Exception as e:
            return self._get_result_status(success=False,
                                           message='Error in get features.')

    def _get_field_types(self, input_type):
        field_type_map = {
                              "string": {
                                            "type": "esriFieldTypeString",
                                            "sql_type": "sqlTypeNVarchar"
                                        },
                              "single": {
                                            "type": "esriFieldTypeDouble",
                                            "sql_type": "sqlTypeFloat"
                                        },
                              "double": {
                                            "type": "esriFieldTypeDouble",
                                            "sql_type": "sqlTypeDouble"
                                        },
                              "oid":    {
                                            "type": "esriFieldTypeOID",
                                            "sql_type": "sqlTypeInteger"
                                        },
                              "date":   {
                                            "type": "esriFieldTypeDate",
                                            "sql_type": "sqlTypeOther"
                                        },
                              "integer":{
                                            "type": "esriFieldTypeInteger",
                                            "sql_type": "sqlTypeInteger"
                                        },
                              "geometry": {
                                              "type": "esriFieldTypeString",
                                              "sql_type": "sqlTypeNVarchar"
                                          }
                         }
        default_type_response = (input_type, "sqlTypeOther")
        if not input_type.lower() in field_type_map:
            return default_type_response
        else:
            return (field_type_map[input_type.lower()]['type'], field_type_map[input_type.lower()]['sql_type'])

    def _create_service(self, portalurl, feature_service_name, portal_username,
                        desc, tags, summary, credits, service_definition, extent,
                        spatialReference, folder_id):
        token = self._get_portal_token()
        # Change the URL depending on account used to create the service
        create_service_url = portalurl + "/sharing/rest/content/users/" + portal_username +"/createService"
        if folder_id:
            create_service_url = portalurl + "/sharing/rest/content/users/" + portal_username + "/"+ folder_id+ "/createService"
        service_definition['name'] = feature_service_name
        service_definition['serviceDescription'] = desc
        service_definition['description'] = desc
        service_definition['initialExtent']['xmin'] = extent.XMin
        service_definition['initialExtent']['ymin'] = extent.YMin
        service_definition['initialExtent']['xmax'] = extent.XMax
        service_definition['initialExtent']['ymax'] = extent.YMax
        service_definition['initialExtent']['spatialReference']['latestWkid'] = spatialReference.factoryCode
        request_params = {
                    "createParameters": json.dumps(service_definition),
                    "outputType": "featureService",
                    "f": "json",
                    "token": token,
                    "description": desc,
                    "snippet": summary,
                    "everyone": True
            }
        try:
            results = requests.post(create_service_url, request_params, verify=False)
            create_results = results.json()
            if create_results.get('success'):
                itemid = create_results.get('itemId')
                serviceurl = create_results.get('serviceurl')
                log_message = "New service created with item ID "+ itemid
                return self._get_result_status(success=True, message='',
                                               item_id=itemid, serviceurl=serviceurl)
            else:
                return self._get_result_status(success=False, message="Unable to create new service. Please check if service already exists.")
        except Exception as e:
            return self._get_result_status(success=False, message=str(e))

    def _add_to_definition(self, serviceurl, fields, indexes, layer_name, shape_type,
                           feature_definition, extent, spatialReference):
        token = self._get_portal_token()
        feature_definition['layers'][0]['name'] = layer_name
        feature_definition['layers'][0]['fields'].extend(fields)
        feature_definition['layers'][0]['indexes'].extend(indexes)
        object_id_field = [i['fields'] for i in indexes if i['isUnique']][0]
        feature_definition['layers'][0]['objectIdField'] = object_id_field
        feature_definition['layers'][0]['geometryType'] = 'esriGeometry' + shape_type.title()
        feature_definition['layers'][0]['extent']['xmin'] = extent.XMin
        feature_definition['layers'][0]['extent']['ymin'] = extent.YMin
        feature_definition['layers'][0]['extent']['xmax'] = extent.XMax
        feature_definition['layers'][0]['extent']['ymax'] = extent.YMax
        feature_definition['layers'][0]['extent']['spatialReference']['latestWkid'] = spatialReference.factoryCode
        definition_add = serviceurl.split("rest")
        definition_add_url = definition_add[0]+"rest/admin" + definition_add[1] + "/addToDefinition"
        definition_params = {
            "f": "json",
            "addToDefinition": json.dumps(feature_definition),
            "token": token
        }
        try:
            results = requests.post(definition_add_url, definition_params, verify=False)
            definition_addition_response = results.json()
            definition_addition_status = definition_addition_response.get('success')
            if not definition_addition_status:
                return self._get_result_status(success=False, message=definition_addition_response['error']['message'])
            return self._get_result_status(success=True, message='')
        except Exception as e:
            return self._get_result_status(Success=False,
                                           message='Unable to add service definition.')

    def get_feature_service_layer_url(self, feature_service_url):
        token = self._get_portal_token()
        params = {
                     "f": "json",
                     "token": token
                 }
        layers = []
        try:
            response = requests.get(feature_service_url, params=params, verify=False)
            response_json = response.json()
            layers = response_json.get('layers')
            feature_layer = [l for l in layers if l.get('name').lower().strip() == 'exposure points'][0]
            layer_id = feature_layer.get('id')
            return '{}/{}'.format(feature_service_url, layer_id)
        except:
            if layers:
                layer_id = layers[0].get('id')
                if layer_id:
                    return '{}/{}'.format(feature_service_url, layer_id)
            return '{}/0'.format(feature_service_url)

    def _add_features_to_service(self, featuresInput):
        serviceurl, features = featuresInput
        add_features_response = self._add_features_request(serviceurl, features)
        i = 0
        while (i<=5) and not add_features_response.get('success'):
            arcpy.AddMessage(add_features_response.get('message'))
            arcpy.AddMessage('Retrying...')
            add_features_response = self._add_features_request(serviceurl, features)
            i += 1
        return add_features_response

    def _add_features_request(self, serviceurl, features):
        token = self._get_portal_token()
        add_feature_url = serviceurl + "/0/addFeatures"
        add_feature_params = {
            "f": "json",
            "features": json.dumps(features),
            "token": token
        }
        try:
            results = requests.post(add_feature_url,add_feature_params, verify=False)
            add_feature_results = results.json()
            add_feature_content = add_feature_results.get("addResults")
            if not add_feature_content:
                return self._get_result_status(success=False, message=add_feature_results['error']['message'])
            else:
                if not add_feature_content[0]['success']:
                    return self._get_result_status(success=False, message=add_feature_content[0]['error'])
            return self._get_result_status(success=True, message='')
        except Exception as e:
            return self._get_result_status(success=False, message=str(e))

    def _get_fields(self, feature_class_path):
        fields = arcpy.ListFields(feature_class_path)
        fields_json = []
        for field in fields:
            field_type, sql_type = self._get_field_types(field.type)
            field_json = {
                             "name" : field.name,
                             "type" : field_type,
                             "alias" : field.aliasName,
                             "sqlType" : sql_type,
                             "length" : field.length,
                             "nullable" : field.isNullable,
                             "editable" : field.editable,
                             "domain" : field.domain,
                             "defaultValue" : field.defaultValue
                         }
            if 'shape' not in field.name.lower():
                fields_json.append(field_json)
        return fields_json

    def _get_indexes(self, feature_class_path):
        indexes = arcpy.ListIndexes(feature_class_path)
        indexes_json = []
        for index in indexes:
            if 'shape' not in index.fields[0].name.lower():
                index_json = {
                                 "name" : index.name,
                                 "fields" : index.fields[0].name,
                                 "isAscending" : index.isAscending,
                                 "isUnique" : index.isUnique
                             }
                indexes_json.append(index_json)
        return indexes_json

    def publish_feature_service(self, feature_class_path, description, tags,
                                summary, credit, lyr, share_settings, currMap,
                                folder_name='', publish_option='Publish all',
                                service_name=''):
        try:
            if not service_name:
                service_name = os.path.basename(feature_class_path)
            tempFolder = tempfile.gettempdir()
            draftName = os.path.join(tempFolder,service_name+'.sddraft')
            draftName = draftName.replace(os.sep,os.altsep)
            sdName = draftName.replace('.sddraft','.sd')
            if os.path.exists(draftName):
                os.remove(draftName)
            if os.path.exists(sdName):
                os.remove(sdName)
            overwrite_service = False
            if 'overwrite' in publish_option.lower():
                overwrite_service = True

            sharingDraft = currMap.getWebLayerSharingDraft("HOSTING_SERVER", "FEATURE", service_name, lyr)
            sharingDraft.summary = summary
            sharingDraft.tags = tags
            sharingDraft.description = description
            sharingDraft.credits = credit
            sharingDraft.overwriteExistingService = overwrite_service
            sharingDraft.portalFolder = folder_name
            sharingDraft.exportToSDDraft(draftName)


            #arcpy.mp.CreateWebLayerSDDraft(lyr, draftName, os.path.basename(feature_class_path),
                                           #'MY_HOSTED_SERVICES', 'FEATURE_ACCESS',
                                           #copy_data_to_server=True, folder_name=folder_name,
                                           #summary=summary, tags=tags,
                                           #description=description, credits=credit,
                                           #overwrite_existing_service=overwrite_service)
            arcpy.StageService_server(draftName, sdName)
            if 'overwrite' in publish_option.lower():
                r = arcpy.UploadServiceDefinition_server(sdName,'My Hosted Services')
            else:
                r = arcpy.UploadServiceDefinition_server(sdName,'My Hosted Services',
                                                     in_public=share_settings['everyone'],
                                                     in_organization=share_settings['org'],
                                                     in_groups=share_settings['groups'])
            serviceurl = r.getOutput(5)
            security_policy_err_message = 'Please check with your portal'\
                                          ' administrator and make sure '\
                                          'the security policy is set '\
                                          'to allow access '\
                                          'to the portal through HTTPS only.'
            try:
                layerDetails = r.getOutput(7)
                if not layerDetails:
                    return self._get_result_status(
                        success=False,
                        message=security_policy_err_message)
                layers = layerDetails.split(';')
                layerId = layers[0].split('|')[1]
            except Exception as e:
                return self._get_result_status(
                    success=False,
                    message=security_policy_err_message)
            itemId = r.getOutput(3)
            share_response = self.share_portal_item(self._portalurl,
                                                    self._portal_username,
                                                    itemId,
                                                    share_with_everyone=share_settings['everyone'],
                                                    share_with_org=share_settings['org'],
                                                    groups=share_settings['groups'])
            return self._get_result_status(success=True, message='', serviceurl='{}/{}'.format(serviceurl, layerId), itemId=itemId)
        except Exception as e:
            return self._get_result_status(success=False, message=str(e))

    '''def publish_feature_service(self, feature_class_path, service_name,
                                desc, tags, summary, credits, share_settings,
                                shape_type, service_definition, feature_definiton,
                                extent, spatialReference, folder_id=None):
        try:
            create_service_result = self._create_service(self._portalurl,
                                                         service_name,
                                                         self._portal_username,
                                                         desc,
                                                         tags,
                                                         summary,
                                                         credits,
                                                         service_definition,
                                                         extent,
                                                         spatialReference,
                                                         folder_id)
            if not create_service_result['success']:
                return create_service_result
            update_item_result = self.update_portal_item(
                                                  create_service_result['item_id'],
                                                  {"tags": tags,
                                                   "accessInformation": credits})
            if not update_item_result['success']:
                return update_item_result
            serviceurl = create_service_result['serviceurl']
            fields = self._get_fields(feature_class_path)
            indexes = self._get_indexes(feature_class_path)
            add_definition_result = self._add_to_definition(serviceurl, fields,
                                                            indexes,
                                                            service_name,
                                                            shape_type,
                                                            feature_definiton,
                                                            extent,
                                                            spatialReference)
            if not add_definition_result['success']:
                return add_definition_result
            get_features_response = self._get_features(feature_class_path)
            if not get_features_response['success']:
                return get_features_response
            features = get_features_response['features']
            features_subsets = [features[i:i+1000] for i in range(0, len(features), 1000)]
            args = [(serviceurl, feature_subset) for feature_subset in features_subsets]
            count = 0
            with concurrent.futures.ProcessPoolExecutor() as executor:
                for arg, add_features_result in zip(args, executor.map(self._add_features_to_service, args)):
                    if not add_features_result.get('success'):
                        add_features_result['message'] = 'Error in adding the features. {}'.format(add_features_result['message'])
                        arcpy.AddMessage('Error in adding the features. {}'.format(add_features_result['message']))
                        return add_features_result
                    count = count + len(arg[1])
                    arcpy.AddMessage('Added {} rows..'.format(count))
            share_response = self.share_portal_item(self._portalurl,
                                                    self._portal_username,
                                                    create_service_result['item_id'],
                                                    share_with_everyone=share_settings['everyone'],
                                                    share_with_org=share_settings['org'],
                                                    groups=share_settings['groups'])

            return self._get_result_status(success=True, message='', serviceurl=serviceurl,
                                           item_id=create_service_result['item_id'])
        except Exception as e:
            return self._get_result_status(success=False, message=str(e))'''

    def share_portal_item(self, portalurl, username, item_id, share_with_everyone, share_with_org,
                           **additional_share_params):
        try:
            token = self._get_portal_token()
            share_item_url = (self._portalurl +
                              "/sharing/rest/content/users/" +
                              self._portal_username +
                              "/items/" +
                              item_id +
                              "/share")
            params = {
                'token': token,
                'f': 'json',
                'everyone': share_with_everyone,
                'org': share_with_org
            }
            params.update(additional_share_params)
            result = requests.post(share_item_url, data=params, verify=False)
            if result.json().get('error'):
                return self._get_result_status(success=False, message=result.json()['error']['message'])
            return self._get_result_status(success=True, message='')
        except Exception as e:
            self._get_result_status(success=False, message=str(e))

    def add_portal_item(self, item_params, file_path=None, data=None, folder_id=None):
        try:
            token = self._get_portal_token()
            add_item_url = (self._portalurl +
                            "/sharing/rest/content/users/" +
                            self._portal_username +
                            "/addItem")
            if folder_id:
                add_item_url = (self._portalurl +
                                        "/sharing/rest/content/users/" +
                                        self._portal_username + "/" + folder_id +
                                        "/addItem")
            params = {
                        'token': token,
                        'f': 'json'
                     }
            if data:
                params.update({'text': data})
            params.update(item_params)
            if file_path:
                with open(file_path, 'rb') as f:
                    files = {'file': f}
                    result = requests.post(add_item_url, data=params, files=files, verify=False)
            else:
                result = requests.post(add_item_url, data=params, verify=False)
            if not result.json().get('success'):
                message = 'Error in adding item to the portal.'
                if result.json().get('error') and result.json().get('error').get('message'):
                    message=result.json()['error']['message']
                return self._get_result_status(success=False, message=message)
            return self._get_result_status(success=True, message='', item_id=result.json()['id'])
        except Exception as e:
            return self._get_result_status(success=False, message=str(e))

    def publish_vtpk_item(self, item_id, service_name, folder_id=None):
        try:
            token = self._get_portal_token()
            add_item_url = (self._portalurl +
                                "/sharing/rest/content/users/" +
                                self._portal_username +
                                "/publish")
            if folder_id:
                add_item_url = (self._portalurl +
                                "/sharing/rest/content/users/" +
                                self._portal_username + "/" + folder_id +
                                "/publish")
            params = {
                'token': token,
                'f': 'json',
                "itemId": item_id,
                "fileType": "vectortilepackage",
                "outputType": "VectorTiles",
                "publishParameters": '{"name": "'+ service_name +'"}'
            }
            result = requests.post(add_item_url, data=params, verify=False)
            if not result.json().get('services'):
                return self._get_result_status(success=False, message=result.json()['error']['message'])
            else:
                if result.json().get('services')[0].get('serviceurl'):
                    return self._get_result_status(success=True, message='', serviceurl=result.json().get('services')[0]['serviceurl'],
                                                   item_id=result.json().get('services')[0].get('serviceItemId'))
                else:
                    return self._get_result_status(success=False, message=result.json().get('services')[0]['error']['message'])
        except Exception as e:
            return self._get_result_status(success=False, message=str(e))

    def update_portal_item(self,
                     item_id,
                     item_params,
                     data=None):
        token = self._get_portal_token()
        update_item_url = (self._portalurl +
                           "/sharing/rest/content/users/" +
                           self._portal_username +
                           "/items/" +
                           item_id +
                           "/update")
        params = {
            'token': token,
            'f': 'pjson'
        }
        params.update(item_params)
        if data:
            params.update({'text': data})
        try:
            results = requests.post(update_item_url, params, verify=False)
            result_json = results.json()
            if result_json.get('success'):
                return self._get_result_status(success=True, message="")
            else:
                err_message = "Could not update portal item. "
                if(result_json.get('error') and
                   result_json.get('error').get('message')):
                    err_message = (err_message +
                                   result_json.get('error').get('message'))
                return self._get_result_status(success=False,
                                               message=err_message)
        except Exception as e:
            return self._get_result_status(
                success=False,
                message=str(e))

    def list_all_portal_folders(self):
        try:
            token = self._get_portal_token()
            data = {
                'token': token,
                'f': 'json'
            }
            response = requests.get(
                ''.join([self._portalurl, '/sharing/rest/content/users/', self._portal_username]),
                params=data, verify=False)
            return response.json().get('folders')
        except Exception as e:
            err_message = "".join([
                "Error in listing folders for user ",
                self._portal_username])
            return self._get_result_status(success=False,
                                               message=err_message)

    def _get_portal_folder_items(self, folder_id):
        try:
            token = self._get_portal_token()
            search_for_item_url = self._portalurl + "/sharing/rest/search"
            query = "ownerfolder:" + folder_id
            search_params = {
                'q': query,
                'token': token,
                'f': 'json',
                'num': 100
            }
            results = requests.post(search_for_item_url,
                                    search_params,
                                    verify=False)
            return results.json().get('results')
        except Exception as e:
            print(str(e))

    def get_item(self,
                  title,
                  item_type,
                  username=None):
        token = self._get_portal_token()
        search_for_item_url = self._portalurl+"/sharing/rest/search"
        if username:
            search_query = 'title:"'+title+'" AND type:"'+item_type+'" AND owner:"' + username + '"'
        else:
            search_query = 'title:"'+title+'" AND type:"'+item_type+'"'
        search_params = {
            'q': search_query,
            'token': token,
            'f': 'pjson'
        }
        try:
            results = requests.post(search_for_item_url,
                                    search_params,
                                    verify=False)
            search_results = results.json()['results']
            exact_match_item = [item for item in search_results
                                if item['title'] == title]
            if not exact_match_item:
                return None
            item = exact_match_item[0]
            return item
        except Exception as e:
            return None

    def delete_items(self, item_ids):
        try:
            token = self._get_portal_token()
            delete_url = self._portalurl + "/sharing/rest/content/users/" + self._portal_username + "/deleteItems"
            params = {
                            "items": ','.join(item_ids),
                                     "f": "json",
                                     "token": token
                        }
            if item_ids:
                requests.post(delete_url, params=params, verify=False)
        except Exception as e:
            return self._get_result_status(success=False, message=str(e))

    def get_feature_service_details(self, feature_service_url):
        try:
            token = self._get_portal_token()
            get_details_url = feature_service_url
            params = {
                'f': 'pjson',
                'token': token
            }
            response = requests.post(get_details_url, params=params, verify=False)
            return response.json()
        except Exception as e:
            return None

    def get_feature_service_string_fields(self, feature_service_url):
        try:
            feature_service_details = self.get_feature_service_details(feature_service_url)
            if feature_service_details:
                fields = feature_service_details['fields']
                string_fields = [field['name'] for field in fields if field['type']=='esriFieldTypeString']
            return self._get_result_status(success=True, message='', fields=string_fields)
        except Exception as e:
            return self._get_result_status(success=False, message=str(e))

    def move_items(self, folder_id, item_ids):
        token = self._get_portal_token()
        move_item_url = (self._portalurl +
                         "/sharing/rest/content/users/" +
                         self._portal_username +
                         "/moveItems")
        params = {
            'token': token,
            'folder': folder_id,
            'f': 'json',
            'items': item_ids
        }
        try:
            result = requests.post(move_item_url, data=params, verify=False)
            result_json = result.json()
            if(result_json.get('results') and
               result_json.get('results')[0] and
               result_json.get('results')[0].get('success')):
                return self._get_result_status(success=True, message="")
            else:
                err_message = "Could not move portal items. "
                if(result_json.get('error') and
                   result_json.get('error').get('message')):
                    err_message = (err_message +
                                   result_json.get('error').get('message'))
                return self._get_result_status(success=False,
                                               message=err_message)
        except Exception as e:
            return self._get_result_status(success=False,
                                           message="Error while moving item ")