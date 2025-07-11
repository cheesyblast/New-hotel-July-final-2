import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Dashboard Component
const Dashboard = () => {
  const [rooms, setRooms] = useState([]);
  const [upcomingBookings, setUpcomingBookings] = useState([]);
  const [checkedInCustomers, setCheckedInCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Modal states
  const [showCheckinModal, setShowCheckinModal] = useState(false);
  const [showCheckoutModal, setShowCheckoutModal] = useState(false);
  const [showNewBookingModal, setShowNewBookingModal] = useState(false);
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  
  // Form states
  const [checkinData, setCheckinData] = useState({
    advance_amount: 0,
    notes: ''
  });
  const [checkoutData, setCheckoutData] = useState({
    additional_amount: 0
  });
  const [newBookingData, setNewBookingData] = useState({
    guest_name: '',
    guest_email: '',
    guest_phone: '',
    room_number: '',
    check_in_date: '',
    check_out_date: ''
  });

  useEffect(() => {
    initializeData();
  }, []);

  const initializeData = async () => {
    try {
      // Initialize sample data
      await axios.post(`${API}/init-data`);
      
      // Fetch all data
      await Promise.all([
        fetchRooms(),
        fetchUpcomingBookings(),
        fetchCheckedInCustomers()
      ]);
    } catch (error) {
      console.error('Error initializing data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRooms = async () => {
    try {
      const response = await axios.get(`${API}/rooms`);
      setRooms(response.data);
    } catch (error) {
      console.error('Error fetching rooms:', error);
    }
  };

  const fetchUpcomingBookings = async () => {
    try {
      const response = await axios.get(`${API}/bookings/upcoming`);
      setUpcomingBookings(response.data);
    } catch (error) {
      console.error('Error fetching upcoming bookings:', error);
    }
  };

  const fetchCheckedInCustomers = async () => {
    try {
      const response = await axios.get(`${API}/customers/checked-in`);
      setCheckedInCustomers(response.data);
    } catch (error) {
      console.error('Error fetching checked-in customers:', error);
    }
  };

  const handleCheckout = async (customer) => {
    setSelectedCustomer(customer);
    setCheckoutData({ additional_amount: 0 });
    setShowCheckoutModal(true);
  };

  const confirmCheckout = async () => {
    try {
      await axios.post(`${API}/checkout`, {
        customer_id: selectedCustomer.id,
        additional_amount: checkoutData.additional_amount
      });
      
      setShowCheckoutModal(false);
      setSelectedCustomer(null);
      
      // Refresh data after checkout
      await Promise.all([
        fetchRooms(),
        fetchCheckedInCustomers()
      ]);
    } catch (error) {
      console.error('Error during checkout:', error);
    }
  };

  const handleCheckin = async (booking) => {
    setSelectedBooking(booking);
    setCheckinData({ advance_amount: 0, notes: '' });
    setShowCheckinModal(true);
  };

  const confirmCheckin = async () => {
    try {
      await axios.post(`${API}/checkin`, {
        booking_id: selectedBooking.id,
        advance_amount: checkinData.advance_amount,
        notes: checkinData.notes
      });
      
      setShowCheckinModal(false);
      setSelectedBooking(null);
      
      // Refresh all data after check-in
      await Promise.all([
        fetchRooms(),
        fetchUpcomingBookings(),
        fetchCheckedInCustomers()
      ]);
    } catch (error) {
      console.error('Error during check-in:', error);
      alert('Error during check-in. Please ensure the room is available.');
    }
  };

  const handleCancelBooking = async (bookingId) => {
    if (window.confirm('Are you sure you want to cancel this booking?')) {
      try {
        await axios.post(`${API}/cancel/${bookingId}`);
        
        // Refresh data after cancellation
        await Promise.all([
          fetchRooms(),
          fetchUpcomingBookings()
        ]);
      } catch (error) {
        console.error('Error cancelling booking:', error);
        alert('Error cancelling booking. Please try again.');
      }
    }
  };

  const calculateTotal = () => {
    if (!selectedCustomer) return 0;
    const roomCharges = selectedCustomer.room_charges || 500;
    const advanceAmount = selectedCustomer.advance_amount || 0;
    const additionalAmount = checkoutData.additional_amount || 0;
    return roomCharges + additionalAmount - advanceAmount;
  };

  const handleNewBooking = async () => {
    try {
      // Validate required fields
      if (!newBookingData.guest_name || !newBookingData.guest_email || !newBookingData.guest_phone || 
          !newBookingData.room_number || !newBookingData.check_in_date || !newBookingData.check_out_date) {
        alert('Please fill in all required fields');
        return;
      }

      // Ensure dates are in the correct format
      const bookingData = {
        ...newBookingData,
        check_in_date: newBookingData.check_in_date,
        check_out_date: newBookingData.check_out_date
      };

      await axios.post(`${API}/bookings`, bookingData);
      
      setShowNewBookingModal(false);
      setNewBookingData({
        guest_name: '',
        guest_email: '',
        guest_phone: '',
        room_number: '',
        check_in_date: '',
        check_out_date: ''
      });
      
      // Refresh bookings after creating new one
      await fetchUpcomingBookings();
      alert('Booking created successfully!');
    } catch (error) {
      console.error('Error creating booking:', error);
      alert('Error creating booking. Please try again.');
    }
  };

  const getAvailableRooms = () => {
    return rooms.filter(room => room.status === 'Available');
  };

  const getRoomStatusColor = (status) => {
    switch (status) {
      case 'Available':
        return 'bg-green-100 border-green-500';
      case 'Occupied':
        return 'bg-red-100 border-red-500';
      case 'Reserved':
        return 'bg-yellow-100 border-yellow-500';
      default:
        return 'bg-gray-100 border-gray-500';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'Available':
        return '🟢';
      case 'Occupied':
        return '🔴';
      case 'Reserved':
        return '🟡';
      default:
        return '⚪';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Dashboard</h2>
          <p className="text-gray-600">Overview of hotel operations and current status</p>
        </div>
        <button 
          onClick={() => setShowNewBookingModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 flex items-center space-x-2"
        >
          <span>+</span>
          <span>New Booking</span>
        </button>
      </div>

      {/* Room Status - Quick View */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Room Status - Quick View</h3>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {rooms.map((room) => (
            <div
              key={room.id}
              className={`p-4 rounded-lg border-2 ${getRoomStatusColor(room.status)} shadow-sm hover:shadow-md transition-shadow`}
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-lg font-bold text-gray-900">{room.room_number}</h4>
                <span className="text-lg">{getStatusIcon(room.status)}</span>
              </div>
              <p className="text-sm text-gray-600 mb-1">{room.room_type}</p>
              <p className={`text-sm font-medium ${
                room.status === 'Available' ? 'text-green-700' :
                room.status === 'Occupied' ? 'text-red-700' :
                'text-yellow-700'
              }`}>
                {room.status}
              </p>
              {room.current_guest && (
                <div className="mt-2 pt-2 border-t border-gray-200">
                  <p className="text-xs text-gray-500">Guest: {room.current_guest}</p>
                  {room.check_out_date && (
                    <p className="text-xs text-gray-500">Out: {room.check_out_date}</p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Upcoming Bookings */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Upcoming Bookings</h3>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          {upcomingBookings.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              No upcoming bookings
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Guest Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Room
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Check-in
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Check-out
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Contact
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {upcomingBookings.map((booking) => (
                    <tr key={booking.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{booking.guest_name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{booking.room_number}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{booking.check_in_date}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{booking.check_out_date}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{booking.guest_phone}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleCheckin(booking)}
                            className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 transition-colors"
                          >
                            Check In
                          </button>
                          <button
                            onClick={() => handleCancelBooking(booking.id)}
                            className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700 transition-colors"
                          >
                            Cancel
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Checked-in Customers */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Checked-in Customers</h3>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          {checkedInCustomers.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              No customers currently checked in
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Customer Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Room
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Check-in Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Check-out Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Contact
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {checkedInCustomers.map((customer) => (
                    <tr key={customer.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{customer.name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{customer.current_room}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{customer.check_in_date}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{customer.check_out_date}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{customer.phone}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <button
                          onClick={() => handleCheckout(customer)}
                          className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700 transition-colors"
                        >
                          Checkout
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Check-in Modal */}
      {showCheckinModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Check In Customer</h3>
            {selectedBooking && (
              <div className="mb-4">
                <p className="text-sm text-gray-600">Guest: {selectedBooking.guest_name}</p>
                <p className="text-sm text-gray-600">Room: {selectedBooking.room_number}</p>
                <p className="text-sm text-gray-600">Phone: {selectedBooking.guest_phone}</p>
              </div>
            )}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Advance Amount ($)
                </label>
                <input
                  type="number"
                  value={checkinData.advance_amount}
                  onChange={(e) => setCheckinData({...checkinData, advance_amount: parseFloat(e.target.value) || 0})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.00"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notes
                </label>
                <textarea
                  value={checkinData.notes}
                  onChange={(e) => setCheckinData({...checkinData, notes: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows="3"
                  placeholder="Any special notes..."
                />
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowCheckinModal(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmCheckin}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                Confirm Check In
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Checkout Modal */}
      {showCheckoutModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Checkout Customer</h3>
            {selectedCustomer && (
              <div className="mb-4">
                <p className="text-sm text-gray-600">Guest: {selectedCustomer.name}</p>
                <p className="text-sm text-gray-600">Room: {selectedCustomer.current_room}</p>
                <p className="text-sm text-gray-600">Phone: {selectedCustomer.phone}</p>
              </div>
            )}
            
            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-md">
                <h4 className="font-medium text-gray-800 mb-2">Billing Details</h4>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span>Room Charges:</span>
                    <span>${selectedCustomer?.room_charges || 500}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Advance Paid:</span>
                    <span>-${selectedCustomer?.advance_amount || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Additional Charges:</span>
                    <span>${checkoutData.additional_amount}</span>
                  </div>
                  <hr className="my-2" />
                  <div className="flex justify-between font-semibold">
                    <span>Total Amount:</span>
                    <span>${calculateTotal()}</span>
                  </div>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Additional Amount ($)
                </label>
                <input
                  type="number"
                  value={checkoutData.additional_amount}
                  onChange={(e) => setCheckoutData({...checkoutData, additional_amount: parseFloat(e.target.value) || 0})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.00"
                />
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowCheckoutModal(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmCheckout}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Confirm Checkout
              </button>
            </div>
          </div>
        </div>
      )}

      {/* New Booking Modal */}
      {showNewBookingModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Create New Booking</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Guest Name *
                </label>
                <input
                  type="text"
                  value={newBookingData.guest_name}
                  onChange={(e) => setNewBookingData({...newBookingData, guest_name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter guest name"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email *
                </label>
                <input
                  type="email"
                  value={newBookingData.guest_email}
                  onChange={(e) => setNewBookingData({...newBookingData, guest_email: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter email address"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone *
                </label>
                <input
                  type="tel"
                  value={newBookingData.guest_phone}
                  onChange={(e) => setNewBookingData({...newBookingData, guest_phone: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter phone number"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Room *
                </label>
                <select
                  value={newBookingData.room_number}
                  onChange={(e) => setNewBookingData({...newBookingData, room_number: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Select a room</option>
                  {getAvailableRooms().map((room) => (
                    <option key={room.id} value={room.room_number}>
                      {room.room_number} - {room.room_type}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Check-in Date *
                  </label>
                  <input
                    type="date"
                    value={newBookingData.check_in_date}
                    onChange={(e) => setNewBookingData({...newBookingData, check_in_date: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Check-out Date *
                  </label>
                  <input
                    type="date"
                    value={newBookingData.check_out_date}
                    onChange={(e) => setNewBookingData({...newBookingData, check_out_date: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowNewBookingModal(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleNewBooking}
                disabled={!newBookingData.guest_name || !newBookingData.guest_email || !newBookingData.guest_phone || !newBookingData.room_number || !newBookingData.check_in_date || !newBookingData.check_out_date}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                Create Booking
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Guests Component
const Guests = () => {
  const [guests, setGuests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedGuest, setSelectedGuest] = useState(null);
  const [showGuestDetails, setShowGuestDetails] = useState(false);

  useEffect(() => {
    fetchGuests();
  }, []);

  const fetchGuests = async () => {
    try {
      const response = await axios.get(`${API}/guests`);
      setGuests(response.data);
    } catch (error) {
      console.error('Error fetching guests:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchGuestDetails = async (guestEmail) => {
    try {
      const response = await axios.get(`${API}/guests/${guestEmail}`);
      setSelectedGuest(response.data);
      setShowGuestDetails(true);
    } catch (error) {
      console.error('Error fetching guest details:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Upcoming':
        return 'bg-blue-100 text-blue-800';
      case 'Checked-in':
        return 'bg-green-100 text-green-800';
      case 'Completed':
        return 'bg-gray-100 text-gray-800';
      case 'Cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Guests</h2>
          <p className="text-gray-600">Manage guest information and booking history</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {guests.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            No guests found
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Guest Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Phone
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total Bookings
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Completed Stays
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Upcoming Bookings
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Stay
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {guests.map((guest) => (
                  <tr key={guest.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{guest.name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{guest.email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{guest.phone}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{guest.total_bookings}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{guest.total_stays}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{guest.upcoming_bookings}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {guest.last_stay ? guest.last_stay : 'Never'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        onClick={() => fetchGuestDetails(guest.email)}
                        className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition-colors"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Guest Details Modal */}
      {showGuestDetails && selectedGuest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-lg font-semibold">Guest Details</h3>
              <button
                onClick={() => setShowGuestDetails(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="mb-6">
              <h4 className="text-lg font-medium text-gray-900 mb-2">{selectedGuest.name}</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Email:</span>
                  <span className="ml-2 text-gray-900">{selectedGuest.email}</span>
                </div>
                <div>
                  <span className="text-gray-500">Phone:</span>
                  <span className="ml-2 text-gray-900">{selectedGuest.phone}</span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="text-lg font-medium text-gray-900 mb-4">Booking History</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Room
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Check-in
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Check-out
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Booked On
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {selectedGuest.bookings.map((booking) => (
                      <tr key={booking.id} className="hover:bg-gray-50">
                        <td className="px-4 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{booking.room_number}</div>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{booking.check_in_date}</div>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{booking.check_out_date}</div>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(booking.status)}`}>
                            {booking.status}
                          </span>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {new Date(booking.created_at).toLocaleDateString()}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            
            <div className="flex justify-end mt-6">
              <button
                onClick={() => setShowGuestDetails(false)}
                className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Bookings Component
const Bookings = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAllBookings();
  }, []);

  const fetchAllBookings = async () => {
    try {
      const response = await axios.get(`${API}/bookings`);
      setBookings(response.data);
    } catch (error) {
      console.error('Error fetching bookings:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Upcoming':
        return 'bg-blue-100 text-blue-800';
      case 'Checked-in':
        return 'bg-green-100 text-green-800';
      case 'Completed':
        return 'bg-gray-100 text-gray-800';
      case 'Cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">All Bookings</h2>
          <p className="text-gray-600">Manage all hotel bookings and reservations</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {bookings.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            No bookings found
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Guest Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Phone
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Room
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Check-in
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Check-out
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {bookings.map((booking) => (
                  <tr key={booking.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{booking.guest_name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{booking.guest_email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{booking.guest_phone}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{booking.room_number}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{booking.check_in_date}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{booking.check_out_date}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(booking.status)}`}>
                        {booking.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {new Date(booking.created_at).toLocaleDateString()}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

// Rooms Component
const Rooms = () => {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddRoomModal, setShowAddRoomModal] = useState(false);
  const [showEditRoomModal, setShowEditRoomModal] = useState(false);
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [roomData, setRoomData] = useState({
    room_number: '',
    room_type: '',
    price_per_night: 0,
    max_occupancy: 2,
    amenities: []
  });

  useEffect(() => {
    fetchRooms();
  }, []);

  const fetchRooms = async () => {
    try {
      const response = await axios.get(`${API}/rooms`);
      setRooms(response.data);
    } catch (error) {
      console.error('Error fetching rooms:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddRoom = async () => {
    try {
      await axios.post(`${API}/rooms`, roomData);
      setShowAddRoomModal(false);
      setRoomData({
        room_number: '',
        room_type: '',
        price_per_night: 0,
        max_occupancy: 2,
        amenities: []
      });
      await fetchRooms();
    } catch (error) {
      console.error('Error adding room:', error);
      alert('Error adding room. Please try again.');
    }
  };

  const handleEditRoom = async () => {
    try {
      await axios.put(`${API}/rooms/${selectedRoom.id}`, roomData);
      setShowEditRoomModal(false);
      setSelectedRoom(null);
      await fetchRooms();
    } catch (error) {
      console.error('Error updating room:', error);
      alert('Error updating room. Please try again.');
    }
  };

  const handleDeleteRoom = async (roomId) => {
    if (window.confirm('Are you sure you want to delete this room?')) {
      try {
        await axios.delete(`${API}/rooms/${roomId}`);
        await fetchRooms();
      } catch (error) {
        console.error('Error deleting room:', error);
        alert('Error deleting room. Please try again.');
      }
    }
  };

  const openEditModal = (room) => {
    setSelectedRoom(room);
    setRoomData({
      room_number: room.room_number,
      room_type: room.room_type,
      price_per_night: room.price_per_night,
      max_occupancy: room.max_occupancy,
      amenities: room.amenities || []
    });
    setShowEditRoomModal(true);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Available':
        return 'bg-green-100 text-green-800';
      case 'Occupied':
        return 'bg-red-100 text-red-800';
      case 'Reserved':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleAmenityChange = (amenity) => {
    const currentAmenities = roomData.amenities || [];
    if (currentAmenities.includes(amenity)) {
      setRoomData({
        ...roomData,
        amenities: currentAmenities.filter(a => a !== amenity)
      });
    } else {
      setRoomData({
        ...roomData,
        amenities: [...currentAmenities, amenity]
      });
    }
  };

  const commonAmenities = ["WiFi", "TV", "AC", "Mini Fridge", "Room Service", "Balcony", "Bathtub", "Safe"];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Rooms</h2>
          <p className="text-gray-600">Manage hotel rooms and their details</p>
        </div>
        <button 
          onClick={() => setShowAddRoomModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 flex items-center space-x-2"
        >
          <span>Add Room</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {rooms.map((room) => (
          <div key={room.id} className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="relative">
              <img 
                src={room.image_url} 
                alt={`Room ${room.room_number}`}
                className="w-full h-48 object-cover"
              />
              <div className={`absolute top-4 right-4 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(room.status)}`}>
                {room.status}
              </div>
            </div>
            <div className="p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-1">Room {room.room_number}</h3>
              <p className="text-sm text-gray-600 mb-2">{room.room_type}</p>
              <p className="text-lg font-bold text-gray-900 mb-2">Rs.{room.price_per_night}/night</p>
              <p className="text-sm text-gray-600 mb-2">Max Occupancy: {room.max_occupancy}</p>
              <div className="mb-4">
                <p className="text-sm text-gray-600">Amenities: {room.amenities?.join(', ')}</p>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => openEditModal(room)}
                  className="flex-1 bg-blue-600 text-white px-3 py-2 rounded text-sm hover:bg-blue-700 transition-colors"
                >
                  Edit Room
                </button>
                <button
                  onClick={() => handleDeleteRoom(room.id)}
                  className="flex-1 bg-red-600 text-white px-3 py-2 rounded text-sm hover:bg-red-700 transition-colors"
                >
                  Remove Room
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Add Room Modal */}
      {showAddRoomModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">Add New Room</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Room Number *</label>
                <input
                  type="text"
                  value={roomData.room_number}
                  onChange={(e) => setRoomData({...roomData, room_number: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter room number"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Room Type *</label>
                <select
                  value={roomData.room_type}
                  onChange={(e) => setRoomData({...roomData, room_type: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select room type</option>
                  <option value="Single">Single</option>
                  <option value="Double">Double</option>
                  <option value="Triple">Triple</option>
                  <option value="Suite">Suite</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Price per Night *</label>
                <input
                  type="number"
                  value={roomData.price_per_night}
                  onChange={(e) => setRoomData({...roomData, price_per_night: parseFloat(e.target.value) || 0})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter price"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Occupancy *</label>
                <input
                  type="number"
                  value={roomData.max_occupancy}
                  onChange={(e) => setRoomData({...roomData, max_occupancy: parseInt(e.target.value) || 2})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="1"
                  max="10"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Amenities</label>
                <div className="grid grid-cols-2 gap-2">
                  {commonAmenities.map((amenity) => (
                    <label key={amenity} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={roomData.amenities?.includes(amenity)}
                        onChange={() => handleAmenityChange(amenity)}
                        className="mr-2"
                      />
                      <span className="text-sm">{amenity}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowAddRoomModal(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleAddRoom}
                disabled={!roomData.room_number || !roomData.room_type || !roomData.price_per_night}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
              >
                Add Room
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Room Modal */}
      {showEditRoomModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">Edit Room</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Room Number *</label>
                <input
                  type="text"
                  value={roomData.room_number}
                  onChange={(e) => setRoomData({...roomData, room_number: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Room Type *</label>
                <select
                  value={roomData.room_type}
                  onChange={(e) => setRoomData({...roomData, room_type: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="Single">Single</option>
                  <option value="Double">Double</option>
                  <option value="Triple">Triple</option>
                  <option value="Suite">Suite</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Price per Night *</label>
                <input
                  type="number"
                  value={roomData.price_per_night}
                  onChange={(e) => setRoomData({...roomData, price_per_night: parseFloat(e.target.value) || 0})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Occupancy *</label>
                <input
                  type="number"
                  value={roomData.max_occupancy}
                  onChange={(e) => setRoomData({...roomData, max_occupancy: parseInt(e.target.value) || 2})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="1"
                  max="10"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Amenities</label>
                <div className="grid grid-cols-2 gap-2">
                  {commonAmenities.map((amenity) => (
                    <label key={amenity} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={roomData.amenities?.includes(amenity)}
                        onChange={() => handleAmenityChange(amenity)}
                        className="mr-2"
                      />
                      <span className="text-sm">{amenity}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowEditRoomModal(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleEditRoom}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Update Room
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Navigation Component
const Navigation = () => {
  const location = useLocation();
  
  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex space-x-8">
          <Link 
            to="/" 
            className={`px-3 py-2 rounded-md text-sm font-medium ${
              isActive('/') 
                ? 'bg-blue-50 text-blue-700 border-b-2 border-blue-600' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Dashboard
          </Link>
          <Link 
            to="/rooms" 
            className={`px-3 py-2 rounded-md text-sm font-medium ${
              isActive('/rooms') 
                ? 'bg-blue-50 text-blue-700 border-b-2 border-blue-600' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Rooms
          </Link>
          <Link 
            to="/guests" 
            className={`px-3 py-2 rounded-md text-sm font-medium ${
              isActive('/guests') 
                ? 'bg-blue-50 text-blue-700 border-b-2 border-blue-600' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Guests
          </Link>
          <Link 
            to="/bookings" 
            className={`px-3 py-2 rounded-md text-sm font-medium ${
              isActive('/bookings') 
                ? 'bg-blue-50 text-blue-700 border-b-2 border-blue-600' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Bookings
          </Link>
          <a href="#" className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium">
            Reports
          </a>
        </div>
      </div>
    </nav>
  );
};

// Main App Component
function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <BrowserRouter>
        {/* Header */}
        <header className="bg-white shadow-md border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <h1 className="text-xl font-bold text-gray-900 flex items-center">
                    🏨 Hotel Management System
                  </h1>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-500">Welcome, Admin</span>
              </div>
            </div>
          </div>
        </header>

        {/* Navigation */}
        <Navigation />

        {/* Main Content */}
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/rooms" element={<Rooms />} />
            <Route path="/guests" element={<Guests />} />
            <Route path="/bookings" element={<Bookings />} />
          </Routes>
        </main>
      </BrowserRouter>
    </div>
  );
}

export default App;