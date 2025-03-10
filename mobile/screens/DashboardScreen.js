import React from 'react';
import { View, StyleSheet, ScrollView, Dimensions } from 'react-native';
import { Text, Card, Title, Paragraph, Button, IconButton } from 'react-native-paper';
import { LineChart } from 'react-native-chart-kit';
import { Ionicons } from '@expo/vector-icons';

const screenWidth = Dimensions.get('window').width;

// Données mockées pour le tableau de bord
const mockData = {
  todayAppointments: 5,
  patientsNeedingBilan: 8,
  totalPatients: 124,
  upcomingBilans: 3,
  weekAppointments: 23,
  // Données pour le graphique
  appointmentsChart: {
    labels: ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'],
    datasets: [
      {
        data: [4, 7, 3, 5, 6, 2, 0],
        color: (opacity = 1) => `rgba(63, 81, 181, ${opacity})`,
        strokeWidth: 2
      }
    ]
  }
};

const DashboardScreen = () => {
  // Configuration du graphique
  const chartConfig = {
    backgroundGradientFrom: '#ffffff',
    backgroundGradientTo: '#ffffff',
    decimalPlaces: 0,
    color: (opacity = 1) => `rgba(63, 81, 181, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
    style: {
      borderRadius: 16
    },
    propsForDots: {
      r: '6',
      strokeWidth: '2',
      stroke: '#3f51b5'
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.header}>
        <Card.Content>
          <Title style={styles.headerTitle}>Bonjour, Dr Martin</Title>
          <Paragraph>Voici le résumé de votre journée</Paragraph>
        </Card.Content>
      </Card>

      <View style={styles.statsContainer}>
        {/* Statistique: Rendez-vous aujourd'hui */}
        <Card style={styles.statCard}>
          <Card.Content style={styles.statContent}>
            <Ionicons name="calendar" size={24} color="#3f51b5" />
            <View style={styles.statTextContainer}>
              <Paragraph>Rendez-vous aujourd'hui</Paragraph>
              <Title>{mockData.todayAppointments}</Title>
            </View>
          </Card.Content>
        </Card>

        {/* Statistique: Patients besoin de bilan */}
        <Card style={styles.statCard}>
          <Card.Content style={styles.statContent}>
            <Ionicons name="warning" size={24} color="#f50057" />
            <View style={styles.statTextContainer}>
              <Paragraph>Besoin de bilan</Paragraph>
              <Title>{mockData.patientsNeedingBilan}</Title>
            </View>
          </Card.Content>
        </Card>

        {/* Statistique: Patients total */}
        <Card style={styles.statCard}>
          <Card.Content style={styles.statContent}>
            <Ionicons name="people" size={24} color="#4caf50" />
            <View style={styles.statTextContainer}>
              <Paragraph>Total patients</Paragraph>
              <Title>{mockData.totalPatients}</Title>
            </View>
          </Card.Content>
        </Card>

        {/* Statistique: Bilans à venir */}
        <Card style={styles.statCard}>
          <Card.Content style={styles.statContent}>
            <Ionicons name="checkmark-circle" size={24} color="#ff9800" />
            <View style={styles.statTextContainer}>
              <Paragraph>Bilans programmés</Paragraph>
              <Title>{mockData.upcomingBilans}</Title>
            </View>
          </Card.Content>
        </Card>
      </View>

      {/* Graphique des rendez-vous */}
      <Card style={styles.chartCard}>
        <Card.Content>
          <Title style={styles.chartTitle}>Rendez-vous cette semaine</Title>
          <LineChart
            data={mockData.appointmentsChart}
            width={screenWidth - 50}
            height={220}
            chartConfig={chartConfig}
            bezier
            style={styles.chart}
          />
          <Paragraph style={styles.chartDescription}>
            Total de {mockData.weekAppointments} rendez-vous cette semaine
          </Paragraph>
        </Card.Content>
      </Card>

      {/* Actions rapides */}
      <Card style={styles.actionsCard}>
        <Card.Content>
          <Title style={styles.actionTitle}>Actions rapides</Title>
          <View style={styles.actionButtons}>
            <Button
              mode="contained"
              icon="calendar-plus"
              onPress={() => console.log('Nouveau rendez-vous')}
              style={styles.actionButton}
            >
              Nouveau RDV
            </Button>
            <Button
              mode="outlined"
              icon="sync"
              onPress={() => console.log('Synchronisation')}
              style={styles.actionButton}
            >
              Synchroniser
            </Button>
          </View>
          <View style={styles.actionButtons}>
            <Button
              mode="outlined"
              icon="account-plus"
              onPress={() => console.log('Nouveau patient')}
              style={styles.actionButton}
            >
              Nouveau patient
            </Button>
            <Button
              mode="outlined"
              icon="bell"
              onPress={() => console.log('Notifications')}
              style={styles.actionButton}
            >
              Notifications
            </Button>
          </View>
        </Card.Content>
      </Card>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 10,
  },
  header: {
    marginBottom: 10,
    elevation: 2,
  },
  headerTitle: {
    fontSize: 24,
  },
  statsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginVertical: 10,
  },
  statCard: {
    width: '48%',
    marginBottom: 10,
  },
  statContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statTextContainer: {
    marginLeft: 10,
    flex: 1,
  },
  chartCard: {
    marginVertical: 10,
  },
  chartTitle: {
    marginBottom: 10,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  chartDescription: {
    textAlign: 'center',
    marginTop: 5,
  },
  actionsCard: {
    marginVertical: 10,
    marginBottom: 20,
  },
  actionTitle: {
    marginBottom: 15,
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  actionButton: {
    width: '48%',
  },
});

export default DashboardScreen;