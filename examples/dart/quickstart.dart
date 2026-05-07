// Replace YOUR_API_KEY with your RapidAPI key
// Add to pubspec.yaml: http: ^1.0.0
// Run: dart pub get

import 'dart:convert';
import 'package:http/http.dart' as http;

const String _apiUrl =
    'https://dimensionspot-bodysize-engine.p.rapidapi.com/v1/predict';
const String _apiKey = 'YOUR_API_KEY';

Future<Map<String, dynamic>> predictBodyDimensions({
  required String gender,
  required double heightCm, // accepts cm, converts to mm internally
  required double weightKg,
  double? exactAge,
  String region = 'GLOBAL',
  String bundle = 'FULL_BODY',
}) async {
  final payload = {
    'input_data': {
      'input_unit_system': 'metric',
      'subject': {
        'gender': gender,
        if (exactAge != null) 'exact_age': exactAge,
        'age_category': 'ADULT',
        'input_origin_region': region,
      },
      'anchors': {
        'body_height': (heightCm * 10).round(), // cm → mm
        'body_mass': weightKg,
      },
    },
    'output_settings': {
      'calculation': {
        'calculation_model': 'AUTO',
        'target_region': region,
        'body_build_type': 'CIVILIAN',
      },
      'requested_dimensions': {'bundle': bundle},
      'output_format': {
        'unit_system': 'metric',
        'confidence_score_threshold': 0,
        'include_range_95': true,
        'include_iso_codes': false,
      },
    },
  };

  final response = await http.post(
    Uri.parse(_apiUrl),
    headers: {
      'Content-Type': 'application/json',
      'X-RapidAPI-Key': _apiKey,
      'X-RapidAPI-Host': 'dimensionspot-bodysize-engine.p.rapidapi.com',
    },
    body: jsonEncode(payload),
  );

  if (response.statusCode != 200) {
    throw Exception('API error ${response.statusCode}: ${response.body}');
  }

  return jsonDecode(response.body) as Map<String, dynamic>;
}

void main() async {
  final data = await predictBodyDimensions(
    gender: 'male',
    heightCm: 178.0,
    weightKg: 82.0,
    exactAge: 35.0,
    region: 'EUROPE',
    bundle: 'TORSO',
  );

  final header = data['header'] as Map<String, dynamic>;
  final dimensions = data['body_dimensions'] as Map<String, dynamic>;

  print('Engine: ${header['calculation_model_used']}');
  print('Dimensions returned: ${dimensions.length}\n');

  for (final key in ['chest_circumference', 'waist_circumference_omphalion', 'hip_circumference']) {
    if (dimensions.containsKey(key)) {
      final dim = dimensions[key] as Map<String, dynamic>;
      print('${dim['label']}: ${dim['value']} ${dim['unit']} '
          '(confidence: ${dim['confidence_score']})');
    }
  }
}
