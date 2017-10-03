import json

def get_classification(parsed_json):
    # Gets the first (only) task's annotation's 'values', pulling the first from lists when required
    annotation_values = next (iter (parsed_json['annotations'].values()))[0]['value'][0]

    xleft = annotation_values['x']
    width = annotation_values['width']
    nw = parsed_json['metadata']['subject_dimensions'][0]['naturalWidth']
    return {'xleft' : xleft, 'width' : width, 'nw': nw}

def get_galaxy_metadata(metadata):
    ra = metadata['RA']
    dec = metadata['Dec']
    z = float(metadata['#Published_Redshift'])
    galID = metadata['SVG_filename'].replace(".svg", "")
    elliptical = bool(metadata['elliptical'])
    url = metadata['URL']
    return {'ra' : ra, 'dec' : dec, 'z' : z, 'galID' : galID, 'elliptical' : elliptical, 'url' : url}

def calc_lambda_central(classification):
    # Input is a classification dictionary with x_left, width, and natural window width
    xleft = classification['xleft']
    width = classification['width']
    nw = classification['nw']
    xmin = int((108./1152.)*nw)# These hardcoded pixel values represent the default window sizes
    xmax = int((1081./1152.)*nw)# If the actual window was sized differently, the factor of 'nw' scales the result appropriately
    lambdamin = 380.
    lambdamax = 500.
    lamperpix = (lambdamax - lambdamin) / (xmax - xmin)
    lambdacen = (xleft + (width / 2.) - xmin) * lamperpix + lambdamin
    return lambdacen

def handle(st):
    try:
        parsed_json = json.loads(st)
        classification = get_classification(parsed_json)
        galaxy_metadata = get_galaxy_metadata(parsed_json['subject']['metadata'])
        lambdacen = calc_lambda_central(classification)

        redshift = (lambdacen-393.37)/393.37
        velocity = 300000*redshift
        dist = galaxy_metadata['z'] * 3e5 / 68

        response = {}
        response['galaxy_id'] = galaxy_metadata['galID']
        response['url'] = galaxy_metadata['url']
        response['RA'] = galaxy_metadata['ra']
        response['dec'] = galaxy_metadata['dec']
        response['dist'] = dist
        response['redshift'] = redshift
        response['velocity'] = velocity
        response['lambdacen'] = lambdacen
    except json.JSONDecodeError:
        response = {'error' : "Invalid json"}
    except:
        response = {'error' : "Missing data or invalid classification"}
    finally:
        print(json.dumps(response))